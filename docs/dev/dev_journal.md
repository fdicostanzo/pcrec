# pcrec Development Journal

Append-only log for restart/status recovery. Newest entries at the bottom.
Each entry: date — summary; accomplishments, issues, decisions, next steps.
Cross-reference docs/plan.md step ids (Mx.y) and docs/decisions.md ids (Dn).

---

## 2026-08-09 — Project start: approach approved, M0/M1 kickoff

- APPROACH.md reviewed by Frank: approved, no notes. Proceeding to implementation.
- Created docs/plan.md (grep'able STATE tags — see format header there), this journal,
  docs/decisions.md (ADR-lite).
- Build system: plain GNU make (D2). On Linux `make` is GNU make; `gmake` is the
  BSD/macOS name for the same tool.
- Launched two sonnet subagents in parallel (D5):
  - harness: tests/harness/run.sh + driver.c + docs/testing.md, self-tested against a
    hand-written stub matcher before the real compiler exists.
  - corpus: tests/base/*.rxt covering base-tier constructs only, every expectation
    cross-verified against python3 `re` (semantics match PCRE for the base tier).
- Main session implementing M1 core: arena/strbuf, base parser with module hook
  points, priority-Thompson NFA, leftmost-first subset construction (accept-pruning,
  D3), byte equivalence classes, computed-goto DFA codegen, pcrec_compile() library
  API, CLI.
- Known M1 semantic limitations recorded in plan.md (mid-pattern `$`, O(n·m)
  unanchored scan until M2, no minimization yet, captures span-only).

## 2026-08-09 — M0 + M1 complete: base compiler end-to-end, 333/333 tests green

Accomplishments:
- Full M1 pipeline working: base parser → priority Thompson NFA → priority subset
  construction (D3) → byte equivalence classes → computed-goto DFA codegen → CLI +
  libpcrec.a. `make test`: 333 cases passed, 0 failed, first integrated run.
- Semantic probes verified against PCRE behavior by hand: a|ab vs ab|a preference,
  lazy quantifiers (a+?, .*?b), `$` end-or-before-final-\n, anchors, empty matches,
  bounded repeats. All exact.
- Harness (sonnet subagent) verified to FAIL correctly on wrong expectations
  (file:line report, exit 1). Corpus (sonnet subagent) 13 files, all expectations
  python3-re cross-verified. CLAUDE.md files: root + docs by main session,
  10 subdirectory files by haiku subagent.
- Compile speed: ~3 ms/pattern including process spawn (100-pattern loop, 0.29 s
  wall) — req. 11 comfortably met at this stage.
- Diagnostics: clean "requires module 'X'" errors for all out-of-tier constructs
  (\d, lookaround, (?i), possessive, POSIX classes, \x{...}); syntax errors carry
  pattern offsets.

Issues / notes:
- One -Wclobbered warning fixed by copying options into a setjmp-safe local.
- `{m,n}` compiles as chained optionals (language-equivalent for span-only
  matching; nested form needed when captures land in M4).
- Empty-match callers must advance manually (documented hazard for the future CLI
  grep mode; the harness driver does single-shot searches only).

Next steps (M2): required-literal/memchr prefilters, first-byte sets, anchoring
fast path (skip the per-start loop), Hopcroft minimization, alternation→trie
factoring, long-text + compile-speed benchmarks as regression tests.

## 2026-08-09 — Subagent final reports: oracle-divergence notes for M7

Corpus agent flagged two python-re vs real-PCRE divergences (cases excluded from
the corpus rather than baking in wrong semantics; revisit when libpcre2 becomes
the oracle in M7):
- `a{,3}`: modern python re treats it as quantifier {0,3}; PCRE treats it as a
  literal. pcrec follows PCRE (literal) — currently untested by the corpus.
- `a++`: python 3.11+ accepts possessive quantifiers; base-tier pcrec rejects
  with "requires module 'atomic-groups'". Corpus uses `a{2}{3}` for the
  multiple-repeat perr case instead.
Harness agent notes: gcc-build failures of generated code are reported as
distinct "HARNESS FAILURE" lines (codegen bugs don't masquerade as N wrong-answer
cases); compile-failure counting is per pattern block.

## 2026-08-09 — Checkpoint review R1 launched (D6)

Four adversarial sonnet critics running over M0+M1: semantics (differential
fuzz vs python re + hand-crafted traps), robustness (ASan/UBSan, recursion
depth, resource caps, API abuse), architecture (attack APPROACH.md claims:
islands, UTF-8×priority-DFA, streaming, codegen-size vs compile-speed),
process (coverage holes, harness quality, docs accuracy). Results to be
compiled into docs/reviews/2026-08-09-m1.md, criticals fixed before M2.

## 2026-08-09 — R1 checkpoint review compiled; all fix-now items applied; 353/353

Full compilation + triage: docs/reviews/2026-08-09-m1.md. Panel of 4 unfriendly
critics (semantics, robustness, architecture, process) delivered 29 findings; 18
fixed same-day, rest became plan steps / design-debt ledger entries. Highlights:
- WRONG-ANSWER bugs (semantics critic, verified vs real libpcre2): mid-branch `$`
  silently dropped matches (`a$\n`), and `$` priority was violated (`$|\n` → 0 1
  instead of 0 0). Root cause: make_state discarded the eol-closure thread list.
  FIX: EOL-variant states — the eol-view is interned as its own DFA state
  (accept + transitions), generated code switches to it exactly at EOL positions.
  Side effect: mid-pattern `$` limitation REMOVED entirely.
- CRASHES (robustness+process): parser recursion (60k nesting) and compile_ast
  left-spine recursion (flat 100k literal — cap checked only after the stack was
  blown). FIX: 250-deep nesting cap + iterative CAT/ALT spine flattening.
- LEAKS on ctx_fail paths (~860 B/failing compile, ASan+RSS confirmed). FIX:
  dfa scratch + nfa patch lists moved to arena; ASan now clean over 1000 fails.
- PCRE parity: quantified bare anchors now rejected (PCRE2 err 109 wording),
  `\x` requires a hex digit (err 178); `(^)*` stays legal. LLP64: generated code
  uses size_t + sentinel, no long.
- Harness integrity: perr == exit 1 only (crash detection), hard errors on
  unparseable lines, zero-case floors, timeouts, -Wall -Wextra -Werror on
  generated code. verify_rxt.py committed to tests/harness/ (P-C3).
- CLI: `--` end-of-options (patterns starting with '-'), missing-value errors.
- Architecture findings reshaped M2 (see plan): search-from-anywhere automaton
  (measured O(n²) today), hybrid emitter (gcc superlinear on computed goto:
  2048 states = 63 s at -O2), bench with gcc-time budgets, PCRE2-oracle fuzzing
  pulled forward to M2.5. APPROACH amended: accept-list islands restricted to
  monotone-preference fragments (A-1), streaming = int-state dispatch loop with
  PARTIAL vs WINDOW_EXCEEDED contract (A-4/A-5).
- New regression file tests/base/review_r1.rxt (+18 cases incl. 2 pcre2-only).
  Suite: 353/353 green; python oracle 351/351 (2 justified skips).
- RECOMMENDED to Frank (not done unilaterally): git init + initial commit — the
  process critic is right that there is no history safety net.

## 2026-08-09 — Published to GitHub

Public repo: https://github.com/fdicostanzo/pcrec (MIT license). Initial commit
= M0+M1+R1 state, 43 files. Root CLAUDE.md now carries the repository-scope
mandate: this project touches only this repo; subagent briefs must restate it.

## 2026-08-09 — M2 core: O(n) engine + table emission + bench/coverage/fuzzer

Engine rework (M2.0 design gate executed per D7):
- Assertion-free patterns → new ENG_UNANCH: one forward pass (priority DFA
  wrapped in lowest-priority self-loop → leftmost-first match END), one reverse
  pass (non-pruning reversed-pattern DFA → match START). Emission table-driven
  (short tables + generic loop) with memchr/bitmap start-state prefilter.
  ^/$ patterns remain on the M1 computed-goto attempt engine (documented gap).
- Measured: R1 A-2's `a*b` worst case 7.8 s/160 KB → 136 µs/4 MB (~25 GB/s via
  autovectorized skip loop; the reverse pass recovers exact spans). Literal
  search 2.1 GB/s on 8 MB (memchr). R1 A-3's `[01]*1[01]{12}`: gcc 29 s/DNF →
  0.11 s at -O1 AND -O2 (~270x). Caps now per-engine (goto 10k / table 32k,
  bounded by table entries). ASan clean on new paths.
- Suite green throughout: 463 harness + 41 CLI cases; python oracle 455/455.

Subagent deliverables (sonnet x3, all green):
- M2.3 bench (tests/bench/): compile-speed, gcc-time (A-3 guard), throughput +
  linearity (A-2 guard) budgets — all PASS on new engine. Known nit: sub-ms
  samples make ratios noisy; drivers support iterations, script should use them.
- M2.4 coverage (tests/cli/ + 3 corpus files + ms/ns startpos directives in the
  harness/driver/verifier). New oracle divergence found: python re clamps
  past-end pos for nullable patterns; pcrec/PCRE2 reject (pcre2-only cases).
- M2.5 fuzzer (tests/fuzz/): PCRE2 oracle via dlopen (no -dev package), its own
  mlimit handling (PCRE2 match-limit ≠ nomatch — subtle oracle bug the agent
  caught itself). Findings: (1) REAL pcrec bug — {,n} is {0,n} since PCRE2
  10.43; FIXED in parse.c same-day + tests/base/fuzz_regressions.rxt. (2) PCRE2
  10.46 optimizer quirk — anchor inside a {0}-quantified group wrongly anchors
  the whole pattern; pcrec + python follow declared semantics; classified as
  intentional divergence bucket in fuzz.py, candidate upstream report to PCRE2.
- Final differential runs: seeds 1/2/3 x 300 patterns, ~5600 pairs, ZERO
  divergences against real PCRE2 on the new engine.

Remaining in M2: M2.1 tail (anchored fast path, interior-literal memmem),
M2.2 (Hopcroft + trie factoring), then checkpoint review R2.

## 2026-08-09 — Upstream-issues tracker + cross-engine perf comparison started

- Created docs/upstream_issues.md (Frank's request): U1 PCRE2 {0}-anchor
  optimizer quirk (suspected-bug, candidate upstream report), U2 python {,}
  divergence, U3 python pos-clamping, U4 PCRE2 match-limit (not-a-bug, oracle
  hazard). Linked from docs/CLAUDE.md and testing.md exclusions.
- Launched compare subagent (sonnet): tests/bench/compare/ — pcrec vs
  pcre2-interp vs pcre2-jit (if available) vs python-re on identical buffers,
  9-case matrix incl. pathological and short-subject regimes; agreement check
  before timing; results snapshot per machine.

## 2026-08-09 — M2.1 tail + M2.2 complete; K1 bug found, documented, deferred

- M2.1: self-loop skip states (up to 4 per machine, forward AND reverse) —
  any state that stays put on >=192/256 bytes gets a SIMD-friendly skip loop,
  generalizing the start-state prefilter. Motivated by compare case h.
  Measured: `.*=.*` over 1 MB key=value 128 -> 1423 MB/s (11x). Anchored fast
  path: `^`-only patterns emit start_max=0 (no start-position loop).
- M2.2: src/opt/minimize.c (Moore signature refinement; EOL-view as an extra
  alphabet symbol). `[01]*1[01]{8}` 512 -> 768 states listed post-merge across
  fwd+rev machines; `.*=.*` collapses to 2 states. Alternation-to-trie
  deferred with rationale (subset construction already merges prefixes).
- Suite 463 + 41 green; bench budgets pass; ASan clean; fuzz seeds 1-4 zero
  divergences.
- K1 FOUND (fuzz seed 3, minimized): `(?:$|[^abc]){2,}` on "XY$\n" -> pcrec
  [0,4), PCRE2/python [0,3). Zero-width `$` loses priority to a consuming
  alternative inside a quantified group; root cause is the ε-cycle guard
  cutting the empty iteration before group-exit ACCEPT. Verified PRE-EXISTING
  (reproduces with minimization disabled), ENG_ATTEMPT-only. Documented in
  new docs/known_issues.md; failing regressions in tests/known_fail/ (excluded
  from `make test` so the suite stays honest); fuzz.py excludes the shape;
  scheduled as plan step M2.6 with the M6 assertions work.

## 2026-08-09 — Clean-box cross-engine BASELINE after M2.1/M2.2

compare tool fixes landed (per-engine DNF no longer drops a case; early-match
metric honesty note at <80% buffer scanned; case (d) subject made wordy so
[a-z]+ can't backtrack over the whole buffer; CASES= subsetting env var).
Agent correctly pushed back that case (h)'s match genuinely spans the full
buffer, so the early-match rule rightly doesn't fire there — my grouping of
(d) and (h) was wrong.

Full 9-case run on a QUIET box (load 0.85), engine = post-M2.1/M2.2:
- vs PCRE2 interpreter: pcrec faster on 7 of 8 comparable cases (3.6x planted
  literal, 11x alternation-absent, 13x email class, 1.8x .*=.*, 7.4x latency);
  interpreter DNF'd (>90 s) on case (e) `a*b`/all-'a' where pcrec does
  24 GB/s. Loses only case (f) (state-heavy [01]*1[01]{8}, 0.15x).
- vs PCRE2 JIT: pcrec WINS latency (61 ns vs 76 ns/call) and case (e) (7.9x).
  JIT still ahead on long-text raw scanning (a/b ~0.15x, d 0.5x, c 0.68x).
- vs python re: ahead everywhere except (f) and (h).
- M2.1 impact visible: (h) `.*=.*` 128 -> 1314 MB/s vs the provisional run.
- Open perf item: case (f) is our weakest — big-table cache behavior on
  state-heavy patterns; minimization alone didn't fix it. Candidate for M2
  follow-up or M3+ (worth an entry when scoped).
Snapshot committed as the baseline (supersedes the load-compromised one).

## 2026-08-09 — Checkpoint review R2 launched (D6)

Five adversarial critics over everything since R1: (1) engine semantics —
attack the D7 forward+reverse construction, minimization behavior-preservation,
skip states, anchored fast path, {,n}; (2) robustness — ASan/UBSan on new
paths, minimize.c allocation, short-typed tables, generated-code boundaries;
(3) benchmark methodology — attack the just-published baseline claims and the
bench budgets; (4) architecture — D7 vs M3 streaming readiness, deferred trie
rationale, case (f) weakness; (5) process/tests/docs — known_fail exclusion,
coverage of new features, doc accuracy. Results → docs/reviews/2026-08-09-m2.md

## 2026-08-09 — R2 complete: 3 wrong-answer bugs fixed, perf claims corrected

Full review + triage: docs/reviews/2026-08-09-m2.md. 4 of 5 critics reported
(process/tests/docs critic died without delivering — lens carried to R3).

FIXED (all verified: 479 harness + 41 CLI, 471/471 oracle, 6 fuzz seeds, bench
budgets, ASan clean):
- R2-S1 + K1 + R2-A1 — ONE closure fix. Loop-entry states are marked; on ε
  re-entry the closure follows the loop EXIT once (PCRE's empty-iteration
  rule). `(?:|a)*` on "a" now [0,0) like PCRE2/python. K1 landed 4 milestones
  early; its regressions moved from tests/known_fail/ to tests/base/ PASSING.
  My K1 scoping claim ("ENG_ATTEMPT only") was FALSE — two critics falsified it.
- R2-M1 (found by me while validating) — lazy bounded repeats with an
  alternation body picked the wrong span; `{m,n}` chained-optionals encoding is
  language-equivalent but NOT preference-equivalent to PCRE's nested form. Now
  nested (iterative). This falsifies a claim R1's critic had cleared.
- R2-R1 memcpy-from-NULL UB (unblocks -fsanitize=undefined).
- R2-P1 fuzzer was NOT deterministic per seed despite documenting it: seeded
  generation ran inside worker threads sharing global random, so interleaving
  chose the corpus. A reported divergence could be unreproducible — it happened
  to me mid-review. Now pre-generated in the main thread; seeds reproduce
  exactly. (All three tools already used fixed seeds — the seed was never the
  problem, the consumption order was.)
- R2-P2 fuzzer bucketed PCRE2 err 120 "regex too large" (PCRE2's own ceiling)
  as a divergence; now its own bucket like our state cap.
- DOC honesty: the "7 of 8 cases" headline was wrong (case g is a TIE — ratio
  0.820-1.113 over 7 runs); "61ns vs 76ns" carried false precision (direction
  robust, magnitude ~1.0-2.0x); capture + case-insensitivity scope gaps now
  disclosed in the compare README.

NOT FIXED — new plan steps: M2.7 engine unification (R2-A2 FATAL: `$` without
`^` routes to ENG_ATTEMPT, no scan-avoidance, still O(n²) — measured 14.3x
slower and quadratic on `a*b$`; R1's A-2 is only HALF fixed and our docs said
otherwise), M2.8 NFA-level trie (hard-fails at ~2000 alternations), M2.9 bench
rigor (no pinning; budgets 9x-300,000x loose), M2.10 dense-pattern codegen
(case f: serial dependency chain, not cache/branch — both ruled out by
measurement), M3.0 now a DESIGN GATE (reverse start-finding cannot stream).

## 2026-08-09 — R2 process critic reported late; findings folded in

The fifth critic delivered after I had closed the triage — strongest report of
the panel. Corrected my review doc (it wrongly recorded the lens as uncovered).

Its headline finding (R2-PR3): SABOTAGE TESTING showed 3 of 6 M2 features
could be completely disabled with ZERO signal — skip states, anchored fast
path, and minimization all left `make test` and `make bench` fully green.
FIXED: new tests/codegen/run_codegen_tests.sh asserts each optimization's
signature in emitted code, and every check was validated by re-running the
critic's exact sabotages (all 3 now FAIL the codegen suite while the
correctness corpus correctly stays green).

Also fixed: git hygiene (tests/fuzz/failures/ and __pycache__ were committed
despite docs saying otherwise; .gitignore updated), 4 doc mismatches
(testing.md claimed the CLI tests weren't in the Makefile — they are;
docs/CLAUDE.md omitted known_issues.md; root CLAUDE.md omitted src/opt/;
tests/CLAUDE.md omitted known_fail/), the oracle now reports its PCRE2 version
(--version) and records it in every fuzz run — previously a different
libpcre2 could have become silently wrong ground truth — and the "mlimit"
bucket is renamed "inconclusive" since it covered any rc != -1, not just
match-limit.

Fuzzer strengthened against the class that produced R2-M1: branch-straddling
subject sampler + preference-trap templates (~8%). My first two attempts at
this were WRONG (subjects taken from the discarded AST node; then drawn from
pattern_alphabet(), which includes metacharacters, so traps were tested
against ":" and "|"). Validated properly at the end: against a build with the
loop-entry fix reverted the improved fuzzer finds 13 divergences where it
previously found 0, and stays clean on the fixed build.

Measurement also partly REFUTED the critic's (explicitly SUSPECTED) diagnosis
of why fuzzing missed R2-M1: the sampler could produce the exposing subject
and the generator does produce the shape ~1% of the time, so the miss was
joint probability, not one structural blind spot.

Accepted process critique: I closed known_issues.md to "no open confirmed
bugs" while 4 of 5 lenses were still outstanding — premature framing.

## 2026-08-09 — M2.7: `$` patterns moved to the O(n) engine (R2-A2 closed)

The largest gap R2 found is fixed. Engine selection is now nfa_has_bot()
instead of nfa_has_asserts(): `$` only needs the per-state EOL variant the
subset construction already computes, applied in BOTH machines at EOL
positions, guarded by `pos + 1 >= n` so the hot loop stays a tight table walk.
`^` still needs a position-dependent BOT variant in the REVERSE machine
(checked at pp == 0), which we don't build — so `^` patterns stay on
ENG_ATTEMPT (fully-anchored ones already have the start_max=0 fast path, so
the remaining slow shape is `^` on only SOME branches). Recorded as D8.

Measured:
- `a*b$` over all-'a': 0.199 / 0.738 / 2.886 s at 20/40/80 KB (textbook
  quadratic) -> flat ~0.011 s through 160 KB. ~250x at 160 KB, quadratic gone.
- Realistic log pattern with vs without a trailing `$`: 69 vs 66 MB/s (same
  measurement method) — parity, where R2 measured a 14.3x penalty.

Tradeoff taken deliberately: the EOL path omits the memchr prefilter and
self-loop skip loops, because both advance `pos` without consulting accept
flags, which is unsound when a state can accept at an EOL position. Restoring
them there is plan M2.12. Removing the O(n^2) restart was the point of M2.7
and is done.

Verification: 511 corpus + 41 CLI + 9 codegen checks green; python oracle
471+32/100%; fuzz seeds 1/2/3/5 clean; bench budgets pass. New regressions in
tests/base/eol_engine.rxt (32 cases) and two codegen structural checks that
would catch a silent revert to the attempt engine (plus one asserting `^`
patterns correctly still use it).

An amusing note: the first attempt to measure this hung, and the culprit was
quadratic behaviour in my own throughput-test generator (`while sum(len(x)
for x in L)`), not in pcrec.

## 2026-08-09 — Session close (context exhausted); handoff written

State at close: M0, M1, M2.0–M2.7 complete; R1 and R2 checkpoint reviews
complete and triaged. Working tree clean, everything pushed through commit
3249d8f. Suite: 511 corpus + 41 CLI + 9 codegen checks green; python oracle
100%; differential fuzz clean vs PCRE2 10.46 across seeds; bench budgets pass.

Session arc: built the whole project from the approved APPROACH in one
sitting — base compiler (M1), the O(n) forward+reverse engine with
table-driven emission (M2.0/M2.1), DFA minimization (M2.2), the test/bench/
compare/fuzz tooling (M2.3–M2.5), and two adversarial review rounds that
between them found and fixed 5 wrong-answer bugs, 3 crash classes, a leak
class, and several false claims in our own docs.

What the reviews taught, in one line each (full versions in docs/reviews/):
- A "probed and held" verdict is evidence about the probes, not a proof —
  R2 broke a claim R1 had explicitly cleared.
- Scope claims about a bug need evidence too; my K1 "ENG_ATTEMPT only" note
  was false and two critics proved it.
- "Fixed" needs a population, not a checkmark (R1's A-2 was fixed for
  assertion-free patterns only; that took until M2.7 to actually close).
- Behavior-preserving optimizations need structural tests or they have no
  regression net at all (3 of 6 could be silently disabled).
- A test-improvement not validated against a known bug is just a nicer green:
  two of my fuzzer improvements reported "0 divergences" while broken.

Next session: read docs/wake.md first (uncommitted, written for exactly this),
then this journal's tail and `grep STATE:not-started docs/plan.md`.
Recommended next step is M2.8 (alternation trie) or M2.12 (restore prefilters
on the EOL path); M3 must not start before its design gate (M3.0) is resolved.

## 2026-08-09 — M2.8: alternation prefix trie (R2-A4 closed) + a repo-fatal .gitignore bug

Session goal from Frank: finish all of M2, with critic passes on new code and
designs as I go, autonomous operation.

**The headline number.** A 3600-word flat alternation went from a hard failure
("NFA exceeds 20000 states") to compiling in 0.93 s. 500/1000/2000-word lists
went 0.72/2.94/11.09 s -> 0.10/0.21/0.46 s.

**My first diagnosis was wrong, and measuring is what caught it.** I wrote a
design note asserting the quadratic was the per-closure
`memset(seen, 0, nfa->n*2)` in dfa.c. I implemented the fix (generation
stamps), measured, and 2000-branch compile time went 11.09 s -> 11.14 s. No
effect whatsoever.

Instrumenting the closure (perf is unusable here — perf_event_paranoid=4)
found the real cost model. `nfa_wrap_unanchored`'s self-loop keeps the entire
branch-selection split chain live at EVERY subject position, so every epsilon
closure walks every branch:

| branches | visits/closure | total visits |
|---|---|---|
| 500  | 1012.9 | 150 M |
| 1000 | 2023.7 | 601 M |
| 2000 | 4044.9 | 2.36 BILLION |

Exactly 2*nbr, doubling with nbr. The correct model is
Theta(|DFA| * ncls * start-closure size), NOT Theta(|DFA| * ncls * |NFA|).
With a trie: 103.5 visits/closure. NFA state count barely moves (18241 ->
14824, 19%) — the trie's win is fan-out, not size, which is the opposite of
what the M2.2 deferral rationale and my own design note both assumed. The
generation-stamp change is still worth keeping, but only as a second-order
effect once the trie lands (1.08 s -> 0.44 s at 2000 branches).

**Two real soundness bugs in my own design, found before shipping.** I caught
the second while drafting the code, which is the only reason it isn't in the
tree. Both confirmed against python3 `re` AND pcrec's own unfactored output:

- `abc|a|abd` on "abd" is [0,1); naive factoring `a(?:bc|bd)|a` gives [0,3).
- `[ab]p|[bc]x|[ab]xy` on "bxy" is [0,2); `[ab](?:p|xy)|[bc]x` gives [0,3).

The second killed my stated correctness argument. I had written that trie
children are "byte-disjoint, so they can never both match" — false: branches
merge only on bit-IDENTICAL bitmaps, but two DISTINCT groups can still
overlap. Guards and full argument are D9. Both are sabotage-validated: with
the disjointness guard disabled tests/base/alternation_trie.rxt fails 2 cases;
with index-range partitioning disabled it fails 7.

**The NFA cap (D10).** 20000 was simply the wrong limiter — it fired before
the DFA caps, which are the ones grounded in measured emitter cost. Raised to
131072, chosen so the DFA cap binds first across the realistic range: 6000
words compile, 10000 fail on the DFA cap with its actionable message, 20000
fail fast on the NFA cap.

Stack depth used to constrain that number and now doesn't. `clo_visit`
recursed on a split's t2 edge, so an alternation nested one frame per branch;
gcc turned it into a jump at -O2 but NOT at -O0, where 200000 branches
segfaulted and 100000 survived. The safe cap literally depended on the
optimisation level. All tail edges are now explicit loop iterations — verified
at -O0 on a 1,000,000-branch alternation.

**A repo-fatal bug found by accident.** Trying to build a pre-M2.8 binary via
`git archive` kept failing with "No rule to make target build/obj/parse/parse.o".
Cause: `.gitignore` line 4 was an unanchored `core`, which matches the
DIRECTORY `src/core/`. arena.c, compile.c, sb.c and internal.h — the entire
pipeline driver — were never committed. **A fresh clone of the public repo did
not build, and had not since M0.** Fixed to `/core` + `/core.*` and the four
files are now tracked. Worth noting that neither checkpoint review caught this,
because both reviewed the working tree, never a clean clone.

**gcc time, measured because a critic brief asked whether it reframes the
milestone.** It does not: gcc is ~1.6x pcrec's own time and flat across
-O0/-O1/-O2 (3600 words: pcrec 0.82 s, gcc 1.36 s), which is the R1 A-3 table
design working as intended.

Verification: 554 corpus (+43 new) + 41 CLI + 9 codegen green; python oracle
100% (546 cases); fuzz seeds 1/2/3/5/7 clean vs PCRE2; bench 0 budget
failures. New KEYWORD-SCALE bench section guards R2-A4 — validated by running
it against a reconstructed pre-M2.8 build, where it correctly FAILs.

Process note: the emitted C for a flat vs trie-factored 2000-word alternation
is the same size (2594238 B) with the same DFA state count (10796), i.e. the
machines are isomorphic. So M2.8 gets no structural codegen test — there is
nothing structural to assert. Its regression net is the .rxt priority corpus
plus the KEYWORD-SCALE compile budget, which is the honest answer rather than
inventing a check that would pass either way.

Two design critics were dispatched before implementation and had not reported
by the time the work was verified and landed; their findings will be folded
into the R3 checkpoint review rather than held up against this commit.

## 2026-08-09 — M2.12: scan avoidance restored on the `$` path (D11)

M2.7 had put `$` patterns on the O(n) engine but traded away the memchr
prefilter and the self-loop skip loops to get there, because both advance
`pos` without consulting accept flags. The plan entry said the fix was to
bound skips at n-1 instead of n. That is half of it, and the other half cost
me a wrong build.

**The half that was written down.** Bound every skip at n-1; drop the forward
memchr's `return 0` early-out, since the start state's EOL view can still
accept at n-1 or n; give the reverse skip a `pp + 1 < n` entry guard (pp only
decreases, so one guard covers the whole loop).

**The half that was not.** I implemented exactly that, and a differential
sweep of 27 `$` patterns x 69 subjects found **53 divergences** — including
matches lost outright (`.*=.*$` on "xyz=abc\n" -> nomatch, python [0,7)).
Bounding a skip at n-1 means the skip can LAND on n-1, and the loop then
consumed that byte without ever taking its EOL view. I had convinced myself
this couldn't happen — I reasoned that `est == st` whenever a skip could run,
which is true of the PRE-skip position and says nothing about where the skip
stops. Another instance of the R2 lesson: my own argument is not evidence.

Fix: run scan avoidance BEFORE the accept/EOL evaluation rather than after.
That is also correct without EOL — every position a skip passes has the same
state and so the same accept bit, and `last`/`sfound` want the extreme
position, which is exactly where the skip stops — so the per-skip-state
`last = pos` line becomes redundant and is gone.

Crucially, I ran the sweep against the PRE-M2.12 binary first and got 0
divergences, which is what established that I had introduced these rather than
uncovered them. That baseline step is the only reason the diagnosis was quick.

**The two emitters are now one.** M2.7 forked `emit_unanchored_eol` as a
near-copy, and the fork is precisely how the `$` path lost these optimizations
for a whole milestone with nothing failing. Merged back into a single
EOL-aware `emit_unanchored`; non-EOL output is byte-identical across 8 probe
patterns, so the merge is a no-op there.

Measured, 7 trials each, load ~0.95, over 8 MB of log text:

| pattern | before | after |
|---|---|---|
| `ERROR: .*$` | 289-292 (median 291) | 18151-24440 (median 22248) |
| `ERROR: .*` | 13840-24282 (median 23245) | 15242-24439 (median 22797) |

So ~76x on the `$` pattern, with non-overlapping ranges across all 7 runs, and
`$` is now at parity with the same pattern without it. The non-`$` path is a
statistical TIE — an early single-sample reading showed 14443 -> 20471 and I
nearly wrote it up as a 1.4x bonus; repeating the trial killed that claim.
Note the 1.8x spread on the non-`$` rows, which is most of the argument for
M2.9.

**Regression net.** tests/base/eol_scan_avoidance.rxt (53 cases, all shapes
the sweep found, python-verified) and 6 new structural checks in
tests/codegen. Both sabotage-validated, and the contrast is the best argument
for structural tests I have seen on this project: reverting the EOL path to
its M2.7 state fails 6 codegen checks while the corpus still passes 53/53,
because the regression is behavior-preserving by construction. Sabotaging the
ORDER instead (accept before skips) fails the order check AND 7 corpus cases.

Suite after: 607 corpus + 41 CLI + 15 codegen green; oracle 100%; fuzz seeds
1/2/3/5/7/11 clean; bench 0 budget failures.

## 2026-08-09 — M2.9 benchmark rigor, M2.10 dense codegen, M2.11 (part)

### M2.9 — the budgets could not fail (D12)

R2-B4 said the budgets were 9x-300,000x loose. The concrete demonstration: a
build with the memchr prefilter and skip states disabled measures 354/319/318
MB/s on throughput cases (a)/(b)/(c) — 5.4x/68x/5.6x regressions — and the old
budgets of 200/50/50 MB/s **pass all three**. Every budget is now
measured-median/1.75, and that same sabotage now fails all three. That
sabotage is the procedure to repeat whenever the budgets are retuned.

Supporting work, because a tight budget on a noisy measurement is a flaky
test, not a gate: `taskset` pinning (chrt probed, unprivileged here);
BENCH_TRIALS repeats judged on the median with max/min spread printed;
governor/turbo/cores/loadavg captured in the run header.

Two measurements were not measuring what they claimed:
- Case (c) planted a match 4 KB into an 8 MB subject, so a correct engine
  early-exited after 0.05% of the buffer. Its "5,547,850 MB/s" was exit
  latency. The subject is now match-free: 1794 MB/s of real scanning.
- Case (b) and the linearity pair were timed at 0.75 ms and 1.4 ms — mostly
  timer and startup. At 20 iterations case (b) reads 21910 MB/s rather than an
  apparent 10534, and the linearity ratio moved from 2.70 to 3.63 against a
  theoretical 4.0.

### M2.10 — the criterion was wrong, not the opportunity (D13)

R2-A5 reported case (f) as having "no skip-eligible states". True, but the
reason was that `pick_skip_states` demanded a state self-loop on >=192 of 256
BYTES — a rule that quietly assumes wide-alphabet subjects. `[01]*1[01]{8}`'s
hot state self-loops on 2 bytes, which is 100% of the bytes that pattern can
ever encounter. Changing eligibility to stay/live >= 75% gives case (f) +40%
(83.7 -> 116.8 MB/s) and leaves everything else alone — verifiably so: for six
other probe patterns the emitted C is byte-IDENTICAL, which is a much stronger
statement than "the timings looked the same".

Getting there involved a false alarm worth recording. A first experiment
(threshold lowered to 1) appeared to cost the log pattern 24%. Re-measuring
with old/new INTERLEAVED showed completely overlapping ranges — it was noise.
Interleaving is one of the things R2-B3 asked for in M2.9, and it earned its
keep within the hour. It also calibrated the noise floor: `ERROR: .*$` showed
a "-9%" between two builds whose emitted C is byte-identical, so ~10% is not a
signal on this box even at median-of-7.

D7's promised computed-goto-vs-table arbitration, which M2.3 claimed and never
built, is now RESOLVED — by measurement rather than by writing more code.
Micro-benchmark of both dispatch styles over the same 6-state DFA: computed
goto is **2.59x slower** (144 vs 374 MB/s), stable to 0.5% over 5 runs. Six
states is about as small as a useful DFA gets, so there is no crossover to
arbitrate; the unconditional table emitter was right, and M2.3's error was the
claim, not the choice. A data-dependent indirect jump mispredicts on nearly
every byte; a small table is an L1 hit that never mispredicts.

### M2.11 — half done

`tests/known_fail/run_known_fail.sh` (R2-PR8) inverts the verdict on deferred-
bug regressions: still-failing is expected, and a file that starts PASSING is
flagged with instructions to promote it into the live corpus and close its
known_issues.md entry. Wired into `make test`, validated in all three states
(empty directory exits 0, now-passing exits 1, still-failing exits 0). The
directory had ceased to exist after R2 fixed every deferred bug; it is back
with its contract documented.

The other half — a pass/fail gate over tests/bench/compare (R2-PR7) — waits on
M2.9's compare.sh rework, which is in flight.

Suite: 607 corpus + 41 CLI + 17 codegen green; oracle 100%; fuzz 1/2/3/5
clean; bench 0 budget failures under the tightened budgets.

## 2026-08-09 — CORRECTION: M2.10 reverted, and M2.12 shipped a 43% regression

The M2.11 compare gate caught two regressions within an hour of existing, one
of which I had written up in this journal as a 40% IMPROVEMENT. Recording both
in full, because the entry above is wrong and the process failure is the more
useful artifact.

**What the gate found.** Generating its floors produced case (f) = 118.6 MB/s
where the R2 baseline said 159.1. Chasing that:

| build | case (f) |
|---|---|
| pre-session (pre-M2.8) | 158.0 |
| M2.8 | 158.6 / 159.1 |
| M2.8 + M2.12 | 90.8 / 90.9 |
| + M2.10 | 118.7 / 115.9 |
| after both fixes | 158.7 / 158.0 |

So M2.12 cost 43%, and M2.10 recovered part of it while I recorded the partial
recovery as a gain. Every number above has spread 1.01-1.02x — none of this
was noise, and all of it was measurable the moment anyone looked.

**M2.10 reverted.** Widening skip eligibility to a fraction of LIVE bytes is
27% SLOWER on the case it targeted (158.6/159.1 -> 118.7 compare, 159.1/157.5
-> 115.9/115.8 bdriver). My +40% came from a "before" sample of 83.7 where the
true value is ~158 — taken un-interleaved, at load 1.69, never repeated. Two
independent harnesses now agree. I had ALREADY written "a single sample is not
a measurement" twice in this journal, built the interleaving machinery for
exactly this in M2.9 that same session, and then failed to use it on my own
result. Reverted; a codegen check asserts the state stays skip-ineligible so
the idea cannot come back on plausibility alone.

**M2.12's regression, and a false claim.** I wrote that non-EOL output was
"byte-identical across 8 probe patterns". That was true of my FIRST M2.12
draft and false of what I committed: after the divergence sweep I moved the
accept evaluation after the skips UNCONDITIONALLY and never re-ran the
identity check. It hoisted the memchr prefilter above the accept check on the
non-EOL path and cost 43%. Both orders are equally correct without EOL; only
one is fast. The emitter now reorders only when `eol` is set, keeps the in-skip
`last`/`sfound` recording on the non-EOL path, and the 8 patterns are NOW
genuinely byte-identical to pre-M2.12. D11 and D13 carry corrections.

**What actually worked here.** The M2.11 gate is one session old and has
already paid for itself twice. Its design choice — gate pcrec's OWN absolute
per-case numbers rather than cross-engine ratios — is what made the signal
legible; a ratio against PCRE2 would have moved for unrelated reasons and
buried a 25% self-regression in the noise R2-B1 already documented.

**What did not.** Every safeguard that caught this was one I built in the same
session; none of the pre-existing tests noticed, because both regressions were
behaviour-preserving. And the thing that produced the false claim was writing
a verification result into a commit message from memory of an earlier run
rather than re-running it against the code actually being committed.

Standing lesson, now stated as a rule rather than a reflection: a performance
number that appears in a commit message, a decision entry, or this journal
must come from an interleaved, repeated measurement taken against the exact
build being described. If it does not, do not write the number.

Verification after both fixes: 607 corpus + 41 CLI + 17 codegen green; oracle
100%; fuzz seeds 1/2/3/5/7 clean; the 27x69 EOL divergence sweep clean; bench
0 budget failures; compare floors regenerated (case f = 159.070, matching the
R2 baseline's 159.056) and the gate validated in both directions.

## 2026-08-09 — Session close: M2 complete, R3 compiled, hand-off written

**All of M2 is done** — M2.8 through M2.12, no steps left open. Six commits
this session: the alternation trie, EOL scan avoidance, benchmark rigor, the
process ratchets, the corrections to the two regressions those ratchets found,
and the load-aware budget verdicts.

State at close: working tree clean, everything pushed. Suite: 607 corpus + 41
CLI + 17 codegen checks green, known-fail ratchet clean; python oracle 100%
(599 cases); fuzz seeds 1/2/3/5/7 clean vs PCRE2; `make bench` 0 budget
failures on a quiet box; `git clone && make && make test` verified from
scratch.

**R3 is compiled but is self-audit only.** All three dispatched critics failed
to report despite four requests including an explicit final call for partial
findings. That is recorded in docs/reviews/2026-08-09-m2-close.md as a process
finding, and it means the M2 close has NO independent adversarial coverage —
the four areas needing attack are listed there and as plan step R3.2. The
process change for R4 is to dispatch critics at the START of the last work
item rather than after it, and to treat a missing report as blocking rather
than as a footnote.

**The session's real story, in one line each:**
- The two most valuable things built (the compare gate, the tightened budgets)
  immediately caught two regressions I had shipped, one of which I had written
  up as a 40% improvement.
- Every regression this session was behaviour-preserving, and therefore
  invisible to the corpus, the oracle and the fuzzer. That is now three
  consecutive checkpoints where behaviour-preserving change is the blind spot.
- The most serious defect was in packaging, not code: `src/core/` had been
  untracked since M0 and a fresh clone did not build. Two adversarial reviews
  missed it because both reviewed the working tree.
- Two of the milestone's results are NEGATIVE (M2.10's skip eligibility, and
  the shape of D7's dispatch arbitration). Both are recorded with numbers and
  one is protected by a codegen check so it cannot be re-landed on
  plausibility. A milestone that records only wins is not recording honestly.

**Next session**: read docs/wake.md first (uncommitted, rewritten for exactly
this), then this journal's tail and `grep STATE:not-started docs/plan.md`.
Recommended order: R3.2 (the missing adversarial pass) before anything else,
then M3.0 — which is a DESIGN GATE, not code: match-START finding under
bounded memory is an unsolved problem and the reverse pass as built cannot
stream.

## 2026-08-09 — R3 critic panel reports (late), and what they found

All five critics dispatched across M2 eventually reported — every one of them
AFTER I had compiled R3 as "no adversarial coverage" and pushed it. The reports
were worth waiting for. They produced one live wrong-behaviour finding in
shipped code, one live hole in a guard I had added hours earlier, and the best
unguarded-change finding of the project so far.

**F3 — the trie put a 1.3 MB stack requirement where 128 KB used to do.**
`trie_build`'s rule 1 recursed once per branch ending at a node, so
`a|a|...|a` with 9000 duplicate branches recursed 9000 deep and SEGFAULTED at a
1 MB stack. The pre-trie construction handled the same pattern at 128 KB —
its deep recursion was in tail position and gcc turned it into a jump. This
walked back nfa.c's own R-2 hardening, and matters because pcrec is a LIBRARY:
musl's default thread stack is 128 KB. Rule 1 now splits on every accept in one
pass, so recursion is bounded by branch points rather than branch count;
TRIE_MAX_RDEPTH went 4096 -> 256 and is documented AS a stack budget with the
measured 272 B frame behind it. 9000 branches now compile at 64 KB. Guarded by
a new tests/cli case at 512 KB, validated by restoring the recursive form.

The irony is exact: D10 says the NFA cap must be derived from a stated frame
budget rather than the optimiser's mood. I wrote that, then shipped a function
in the same commit whose stack cost I never measured.

**`make bench` exited 0 while gating nothing.** My own LOAD_LIMIT change from
that morning downgraded a budget miss to INCONCLUSIVE on a busy box — correct —
and then exited 0, which was not. A build with a 3.4x/68x/5.5x regression
exited GREEN whenever the box was loaded, and at a default of cores/2 against
observed loads of 5–24, loaded was the normal case. Exit codes are now
three-valued (0 clean / 1 failed / 2 not gated). D14.

**Five nets, all green, on a real regression.** Deleting the bitmap half of the
start prefilter costs ~1.5x on multi-first-byte patterns and passed make test,
make bench, the oracle, the fuzzer and gate.sh. Every bench pattern had exactly
one escape byte, so the bitmap branch had no coverage anywhere — D12's
"sabotage-validated" claim covered half a feature. New case (d) with a
deliberately tighter budget, validated against the critic's exact edit. D15.

**Also settled, from the critics:**
- Skip states have NO throughput guard at all — all four bench patterns emit
  zero skip tables, so bench is byte-identical with pick_skip_states returning
  0. That settles the R3.1 "re-measure on a quiet box" question: no measurement
  was possible. And the cap of 4 buys nothing (730.8 vs 740.1 at cap 1), so
  asserting a COUNT would pin a number no measurement supports. R3.1 reframed.
- My "large for blocklists" claim was overstated: real lists save 25–40%
  (Public Suffix List 28.8%), not "large". This strengthens the conclusion —
  no realistic 3600-word list drops under the old cap by factoring — and the
  corrected figures and their method are now in nfa.c.
- The gcc-time disagreement reconciles: on FLAT patterns pcrec is 14–35x gcc;
  after the trie, gcc becomes the LARGER half (0.79 s vs 1.36 s). My number
  described the shipped state, the critic's the pre-trie one. Consequence
  recorded: M2.9's compile budgets measure only pcrec's half.
- Two comments of mine were simply wrong and are fixed: the contiguous-run rule
  does NOT rest on "first matching branch in index order wins" (D3 keeps
  lower-priority threads alive past an accept on purpose), and "the trie caps
  alternation chains at node fan-out" is false with no shared prefix.
- docs/testing.md still claimed the CLI tests were not wired into the Makefile.
  R2 recorded that as FIXED and it was not; it survived two reviews until a
  critic grepped for it.

**Process lesson, and it is not the one I expected.** I closed the milestone on
self-audit because the panel had not reported, and I was right to record that
as a gap — but I was wrong to treat the gap as merely procedural. The panel
found a live segfault, a hole in a guard I had just built, and a regression
five independent nets missed. Self-audit found the things I was already looking
for. The fix for R4 is not "chase critics harder" but "do not declare a
milestone reviewed until the reports are in hand", which is now written into
the review.

Verification after all fixes: 619 corpus + 42 CLI + 17 codegen green; oracle
100% (611); fuzz seeds 1/2/3/5/7 clean; 27x69 EOL sweep clean; 11,760-case trie
sweep clean; bench 0 budget failures with the new case (d).

## 2026-08-09 — R3 round 2: a 56x compile cliff, and five false claims

The last two critics (semantics, claim-audit) reported after everything above
was pushed. Between them they found one real functional cliff and refuted five
claims I had written. Everything below is fixed and verified.

**The cliff (56x).** `groups_disjoint` was all-or-nothing PER NODE: one
overlapping class pair among the branches at a node sent the whole list to the
unfactored construction. At the root of a keyword list that means zero
factoring for everything. Changing ONE character of ONE branch in a 3600-word
list from `x` to `[ab]` took compile time from **0.80 s to 44.9 s** — the
entire M2.8 win lost to one character, and invisible to KEYWORD-SCALE because
its generated word list contains no classes. D9 had called the fallback
"conservative rather than wrong": correct, and it read as a mild loss when it
is a cliff.

Fixed by splitting the node into maximal contiguous RUNS whose distinct
bitmaps are pairwise disjoint, and chaining the runs in index order — sound for
the same reason the eligible/ineligible run rule is. The offending branch
becomes a run of its own and the other 3599 still factor: 44.9 s -> 0.82 s,
identical to the class-free baseline. The 2%-classes variant went 35.6 s ->
2.9 s. The disjointness test is now an exact O(n) running-union check
(pairwise-disjoint iff each group is disjoint from the union of the earlier
ones), which also removes an `ng > 64` bail that degenerated correct inputs for
no reason.

Verified hard, because this makes overlapping classes factor MORE
aggressively: 619 corpus + 42 CLI + 17 codegen, oracle 100%, fuzz 5 seeds, the
EOL/startpos/trie sweeps, and a new overlap-heavy sweep (31,350 cases over an
alphabet where every class pair intersects) — all clean. Sabotage-verified:
disabling the run split gives 6 corpus failures and 64 sweep divergences.
Guarded by a second KEYWORD-SCALE case carrying 2% classes, which FAILS against
the wholesale-bail build while the class-free case still passes.

**Five claims refuted, all corrected in place:**
1. "Bounded by the flat construction" (D9) is false — the trie can use MORE
   NFA states, one extra N_EPS per branch ending at a node (`bb|a|ba` 10 vs 8).
   Additive, aggregate ratio 0.999, so D10's arithmetic survives; the bound is
   flat + O(branches).
2. My fan-out constants were exactly 2x high (4045 -> 2022 = 1.01*nbr, 103.5 ->
   51.7) from a counter that also counted -1 targets. The 39.1x ratio, and
   every conclusion, is unchanged.
3. D10's "verified at -O0 on a 1,000,000-branch alternation" is VACUOUS: at 1M
   branches the build fails on the NFA cap before any closure runs. The
   conclusion holds; the experiment quoted didn't demonstrate it. The entry's
   own revisit-when is already answered by the parser's 250-deep group cap.
4. "The gate, one commit old, caught two regressions" — wrong twice. gate.sh
   was added in the SAME commit as the fix, and its 0.70 margin fires only
   below 1.43x, so the 27% case was NOT caught by it (I caught that one by
   eye, comparing a floor against R2's published baseline). It caught one.
5. "Every budget is measured-median/1.75" — only 3 of 8. The GCC budgets sit at
   9.13x, inside the "9x-300,000x loose" band D12 opens by condemning.

**Two more holes in my own guards, both fixed.** gate.sh treated an unmeasured
case as SKIP and exited green, so pcrec erroring on 8 of 9 cases reported
"checked: 1, failures: 0" and PASSED — total breakage passing the ratchet. It
now fails when coverage is incomplete. And case (b)'s budget flakes under load
by a shifted distribution rather than variance, which more trials cannot fix.

**What held.** Both critics hammered semantics and found no wrong answer:
~9.5M oracle-checked comparisons between them, four independent sabotage builds
proving each probe had detection power, `clo_visit` equivalence proven by
byte-identical codegen on 4429 patterns, and non-EOL byte-identity confirmed at
**1827** patterns rather than the 8 I claimed. python `re` and PCRE2 agreed on
all 16,568 patterns tested, so the base-tier oracle transfers.

**The pattern across this whole checkpoint**, stated plainly because it recurred
four times: every failure was a MEASUREMENT CLAIM ABOUT A SAFEGUARD, not a
defect in the compiler. The engineering held under 9.5M oracle comparisons. What
did not hold was what I wrote about the things meant to protect it — a gate
credited with a catch it could not make, budgets that did not match their stated
derivation, constants off by 2x, and a guard that read as a mild loss and was a
cliff. Claims about safeguards need the same evidence as claims about code, and
they are exactly where I stopped applying it.

## 2026-08-09 — R3 follow-ups: R3.1, R3.3, R3.4, R3.5 closed

Worked the open items the R3 checkpoint created. Four closed. Each one changed
shape once it was probed rather than reasoned about, and in TWO of them the fix
the review prescribed would not have worked — recorded below, because "the
review said to do X" turned out not to be evidence that X measures anything.

**R3.3 — the trie IS structurally testable, and the check is now the strongest
net in the project.** The M2 journal concluded M2.8 could not have a structural
test, because the trie changes the NFA and the NFA is not an output. That
inverts the actual situation: the trie is required to be OUTPUT-PRESERVING, so a
compiler built with factoring off must emit byte-identical C, and diffing the
two builds tests the soundness rules directly — no subjects, no gcc.
`-DPCREC_NO_TRIE` plus `tests/codegen/run_trie_identity.sh`, 500 generated
alternation patterns in ~4 s, wired into `make test`. D16.

Detection power is not in the same class as what existed. Breaking the
disjointness guard fails 2 cases in the entire 663-case corpus, and 21 of 200
patterns here; breaking rule 1's accept split fails 132 of 200. Each failure
names the pattern rather than a subject that happened to hit it.

The part that mattered most is the part the review did not ask for. An
equivalence check is VACUOUS if both builds have the optimization off — then
everything agrees and the script certifies a deleted optimization, which is
exactly the "guard that cannot fail" shape R3 found twice in guards written the
same day. So there is a POSITIVE CONTROL, deterministic rather than
timing-based: `(<256 8-bit binary strings>){100}` needs ~230k NFA states
unfactored and ~51k factored against a 131072 cap, so the two builds fail at
different STAGES and the stage is visible in the error text. Sabotage-validated
three ways, and the third is the one worth keeping: with the trie disabled in
the shipped build, identity passes 200/200 and the positive control is the ONLY
thing that fires.

Two false starts worth not repeating. The first positive control — 4000 branches
sharing a 30-byte prefix — does not work: the DFA cap bites before the NFA cap
so both builds fail identically, and at 136 KB the pattern also exceeds Linux's
128 KB single-argv limit. And the first differ compared `-o a.c` against
`-o b.c`, so all 500 patterns "differed" on the `#include "a.h"` line. Both
builds now emit to stdout. The second one is the useful lesson: a differential
harness can be 100% wrong in a way that still looks like a finding.

**R3.4 — the hole was real, and the load-bearing case is on the other path.**
The review asked for one pattern from the `a.*|b$` family. Added six (44 cases,
oracle-verified), because measuring which sabotage each pattern catches showed
the named family is not where the detection power is:

- restricting the EOL accept to the boundary fails 3 cases, all `a.*|b$` and
  `a[^\n]*|\n$`;
- dropping the non-EOL post-skip `last = pos` fails 10 cases, all `[a-z].*|q$`,
  `a.*|b` and `=.*|;`;
- the original 13 patterns catch NEITHER.

`[a-z].*|q$` is the interesting one: written with a `$`, it compiles to a
machine with NO EOL variants, because `[a-z].*` subsumes `q$` and no eolvar
survives. That accident is what gives it reach into the non-EOL path — so
`a.*|b` and `=.*|;` were added carrying no `$` at all, and that coverage cannot
evaporate under a construction change.

Also found while validating, and fixed in the file header: this file does NOT
catch relaxing the EOL forward skip bound from n-1 back to n, despite claiming
every case in it failed the first M2.12 attempt. Other tests/base files catch
that one (3 cases).

**R3.1 — the shape the review prescribed measures the wrong thing.** R3 proposed
`.*=.*` over a key=value subject. It matches at offset 0 and ends at 127, so an
8 MB run exits after 127 bytes and reports **32 GB/s** — R2-B4's exit-latency
mistake, inside the very item written to close a coverage gap. Recorded in the
source so it is not tried again.

THROUGHPUT case (e) is `=[^\n]*!` over 8 MB of 128-byte key=value records: no
`!` exists in the alphabet so the scan is full, and ~92% of bytes are consumed
inside the skip loop. Interleaved median-of-9, pinned, load 0.79: healthy 1741.8
MB/s (spread 1.081x), sabotaged 360.6 MB/s (spread 1.030x) — **4.83x**. Budget
1000 MB/s, which is median/1.74 and is stated that way rather than as "/1.75",
because R3 found only 3 of 8 budgets matched the derivation they claimed. The
case also hard-errors if its own pattern ever stops emitting a skip table, so it
cannot quietly decay into a second prefilter measurement — which is precisely
how cases (a)-(d) came to have zero skip coverage.

**R3.5 — per-case margins, and the gate now prints its own blind spot.** One
global 0.70 margin fires only below 1.43x, which is why M2.10's 27% regression
passed this gate while the review credited the gate with catching it. Margins
are now per case, derived from that case's own trial spread as
`clamp(1/(spread*1.05), 0.70, 0.90)`. D17.

The ceiling is the part that needed thinking about: it is NOT derived from the
spread. One run's within-run spread is a sample, not a distribution, and this
box's noise floor is ~10% even at median-of-7 — gating tighter than 0.90 would
manufacture failures out of noise however tight a single run looked. The floor
keeps a noisy case no looser than the old default, so this is never a loss of
strictness.

Measured spreads: a 1.01x, b 1.01x, c 1.02x, d 1.06x, e 1.26x, f 1.09x, g 1.22x,
h 1.04x, i 2.04x — a 2x range that one global margin had to cover with its
loosest member. Validated: a uniform 27% regression now fails **8 of 9** cases
where it previously failed 0. Case (i) (latency, spread 2.04x) still cannot see
it, and the gate now prints `weakest case: a uniform regression must exceed
1.43x to fail this gate` on every run, so that limit is stated by the tool
instead of waiting for a critic to compute it.

Floor VALUES were deliberately NOT re-baselined. The full compare run taken for
the spreads reproduced every recorded value within 2% (a 2201 vs 2192, b 1968 vs
1970, c 390 vs 389, f 158 vs 159, h 1323 vs 1303), so there was nothing to move,
and moving them would have quietly ratcheted the baseline down for no reason.

**Also cleared from R3's NOTED list:** the four directories with no CLAUDE.md
(`tests/bench`, `tests/bench/compare`, `tests/cli`, `docs/reviews`) now have
one. Writing `tests/cli/CLAUDE.md` immediately produced a correction to itself:
the first draft claimed python3 was a hard dependency of `make test` and that
the suite covered the NFA/DFA caps. Neither is true — python3 is used only by
case 8, which SKIPS itself when python3 is absent, and that skip goes to stderr
while the suite still exits 0. Another guard that stops guarding without saying
so; recorded in the file.

**R3.2 remains open and is now the oldest unresolved item.** Two critics were
dispatched at the start of this session against the two areas R3 left unprobed
(the D11 EOL/non-EOL ordering asymmetry, and whether D13's dispatch
micro-benchmark represents the real emitter). Both ran — their oracle sweeps
were visible in the process table — and neither reported. That is the third
consecutive checkpoint at which dispatched critics have failed to deliver, and
it is now clearly a process defect rather than bad luck: the work gets done and
the findings are lost. R4 should not dispatch a critic without a mechanism that
makes a partial report recoverable.

Verification: 663 corpus + 42 CLI + 17 codegen + 3 trie-identity green; python
oracle 100% (655 cases); `make bench` 0 budget failures with the new case (e);
compare gate 9/9 with the new margins; and every new guard sabotage-validated
individually, with the sabotage that each one FAILS to catch recorded next to it.

## 2026-08-09 — R3.2, half closed: D13 probed against the real emitter and HELD

The D13 critic dispatched at the top of the session reported after the R3.1/3/4/5
work was already committed — the same late-report pattern as R3, but this time
the report arrived. It closes item (2) of R3.2. Item (1), the D11 ordering
asymmetry, is still open: that is now TWO critics dispatched at it with no
report, and a third running.

**The micro-benchmark behind D13 does not exist and never did here.** CONFIRMED
myself, not taken on trust: `git log --all -S "dispatch.c"` returns exactly one
commit, and it is the one that added the D13 prose mentioning the file. The
measurement that arbitrated computed-goto vs table dispatch was never checked
in, so it cannot be re-run — only re-derived. Worth generalising: a
decision-critical measurement kept in a scratchpad has a half-life, and this one
had already expired before anyone asked to see it.

**It also does not represent the emitter.** A 6-state single dispatch loop
models neither the forward+reverse double scan, nor the per-iteration
accept/prefilter/skip-branch side work, nor the `fcls[]` equivalence-class
indirection — and for prefilter-eligible patterns most bytes never reach the
dispatch loop at all, which is the whole point of the prefilter. The synthetic
loop measures the path emit_dfa.c works hardest to avoid.

**Re-derived on real emitter output, and the decision holds.** The critic
transformed the emitter's own generated C into computed-goto form (emitter
untouched, results verified identical before timing), 3 patterns, median of 9
interleaved: goto/table 0.35-0.91 on random input, 2.75-3.07 on predictable
input, across a 4x range of both ncls and state count with the direction never
flipping. That reproduces R3-SELF-4's "predictability, not size" correction at
realistic scale instead of on a toy. The critic disclosed that box load ran
0.44 -> 14.49 during its runs, which by D14's own rule is INCONCLUSIVE; I am
recording direction, not precision, and said so in the decision.

**The decisive argument is one D13 never makes.** D13 arbitrates on runtime
alone, but emit_dfa.c and D7 chose tables for compile-time reasons (R1 A-3),
leaving runtime open only for SMALL DFAs. Verified independently on a quiet box
(load 0.95, `gcc -c` only): computed goto costs **10.9x / 35.6x / 319x** more
compile time than tables at 6075 / 2304 / 78705 table entries. The 300-word
alternation takes 0.29 s as a table and **91 s** as computed goto. For large
keyword/dictionary alternations — a normal use of this compiler, not an edge
case — computed goto is disqualified before the runtime question is reached.

My numbers are larger than the critic's (it reported 5.7x/16x/210x); the
difference is full builds vs compile-only, and constant link overhead dilutes
the ratio. Both directions agree, and I recorded which is which rather than
picking the more impressive number.

Two corrections applied to D13: "six states is about as small as a useful DFA
gets, so there is no crossover" overstates what was shown — direction never
flips, but magnitude moves with ncls (0.91 at ncls 3 vs 0.35-0.42 at ncls 27) —
and its revisit-when is widened to name the shape that actually stresses the
question: large alternations with a wide first-byte escape set, whose bitmap
prefilters skip almost nothing, so the disputed loop runs on every byte.

**Process note.** The two critics dispatched at the start of this session were
given no way to deliver partial work, and one of them again produced nothing.
The two dispatched afterwards are required to append findings to a file on disk
as they confirm them, rather than reporting only at the end. That mechanism has
already produced a report file for the guards critic while it is still working.
Building the mechanism beats repeating the instruction — the same lesson R3's
reflection drew about tooling versus remembered principles.

## 2026-08-09 — critics on my own R3 work: 12 findings, most of them my claims

Two critics, this time required to append findings to disk as they confirmed
them. Both delivered. Between them they produced one real hole in a guard I had
just built, one real coverage gap, and eight corrections to claims I had written
that same day. R3's headline lesson — every failure was a measurement claim
about a safeguard rather than a compiler defect — reproduced inside the commit
that quotes it.

**The one that matters: my positive control was satisfied only in the letter.**
`run_trie_identity.sh` had ONE control, at 256 branches, while every generated
pattern had 3..8. A critic broke it in a single clause —
`elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)`, the shape of a
plausible "only factor when it's worth it" heuristic — and got the identity
check green, all three checks green, KEYWORD-SCALE green and the ENTIRE
`make test` green with M2.8 effectively deleted for every hand-written pattern.
The control proved the trie fired for one 256-branch pattern and nothing proved
it fired for anything a user would write.

Fixed with controls at 4, 8 and 256 branches. The small ones have to be
`^`-anchored: without `^` the engine also builds a reverse machine, a shared
PREFIX barely factors in reverse (the reverse trie factors the reversed
branches' prefix, i.e. the original SUFFIX, which is 2 bytes here), so the
reverse NFA blows the cap in both builds and the control degenerates to
unfactored/unfactored. Verified: the critic's sabotage now fails the 4- and
8-branch controls while the shipped tree stays green. D16 now states the rule as
"the control must fire INSIDE the corpus's own range", which is the transferable
half.

**Two sabotage numbers I published were wrong, in two different ways.**
- "~14 patterns in 500" was never measured by me. It was the original R3
  critic's figure for a different corpus, repeated without re-running. The real
  number is 64 — the check is 4.5x stronger than I advertised.
- "rule 1 off -> 132 of 200" came from a CONTAMINATED TREE. My sabotage loop
  reverted between runs with `git checkout` inside a tarball copy that is not a
  git repo; the failure was swallowed by `|| true`, so rule 1's sabotage landed
  on top of rule 2's. 132 is the both-guards-off number. I had already noticed
  and fixed exactly this bug in a different sabotage block earlier the same
  session and did not go back to check the first one.
- Worse, the natural rule-1 sabotage is UB: skipping the accept split leaves
  items with `len == depth` in the list, and rule 2 then reads `seq[depth]` past
  the allocated key — a 32-byte arena over-read, so the count is unstable
  between builds (171 mine, 176 the critic's, same edit). The citable form is a
  memory-safe variant that removes the accepts but hoists them instead of
  partitioning around each: 38 of 200, 94 of 500, and 16 .rxt cases. The recipes
  are now in tests/codegen/CLAUDE.md so every number can be replayed.

**`floors.tsv`'s provenance header was wrong in both halves.** I wrote that the
values come from `results-ubuntubudu-20260809.md`; they match neither recorded
results file (a: 2192.358 vs 2130.050 vs 2201.356) and come from a run not in
the repository. And "reproduced every one of them within 2%" named the five
cases that supported it while case (i) was 10.4% off — the one case whose 0.700
margin means this gate cannot see it move, so the miss was self-concealing.
Carried as [R3.6].

**The "~10% noise floor" that justifies the 0.90 ceiling is not measured
anywhere in this repo.** It appears in D17, gate.sh and floors.tsv. The three
runs the repo does contain move by <=3.3% run-to-run on eight of nine cases.
Writing an unmeasured constant into the decision entry whose subject is not
gating on unmeasured constants is the joke telling itself. The ceiling STAYS at
0.90 — three runs is too thin a basis to tighten a gate on, and tightening on it
would repeat the error rather than fix it — but the justification is now the
recorded data plus an admission of over-conservatism. [R3.7].

**And I re-asserted a claim the previous commit had refuted.** The new
`tests/bench/CLAUDE.md` said "budgets are measured-median/1.75 (D12)". Four of
nine are not (COMPILE 3.60x, GCC_O1/O2 9.13x each, LINEARITY 2.08x); 080d02c
recorded exactly this refutation one commit earlier. The table is now in the
file and [R3.8] carries fixing the budgets. The same sentence still stands
unfixed in run_bench.sh's header and in D12 itself.

Also corrected: the claim that family 8 is "the only family exercising
trie_key's rev path" is false in both directions — every pattern without `^`
builds a reverse machine, so 8 of 9 families are on it at full strength, and
family 8 builds a forward trie too. And the reference build's `-Ilib -Isrc` were
relative while the sources were absolute, so the script only worked from the
repo root.

**What HELD.** The identity check's detection power is real (64/500 and 94/500
against the two guards); the `-Wall -Wextra` check on the reference build does
fire; the "27% regression fails 8 of 9" claim was independently reproduced —
with the caveat, now recorded next to it, that case (e) fails by only 3.4% and
that headline is a property of one sampled spread, not of the design.

## 2026-08-09 — R3.2 fully closed: D11 swept to 25.8M comparisons and held

The second critic delivered the sweep R3.2 had been asking for since the
checkpoint: **25,834,470 oracle-checked comparisons against PCRE2 10.46 over
6432 patterns, 0 divergences** on the shipped compiler, including under
ASan+UBSan with exact-size buffers, every startpos, and the boundary subjects
(empty, single `\n`, all-`\n`, trailing `\n`). It also derived the emitted
order from the generated C and confirmed the prose matches on all four halves.

Both directions of the asymmetry were sabotage-tested with a switch that moves
ONLY the order and is byte-identical to the shipped compiler when neutral.
Forcing the non-EOL order onto the EOL path: 238,144 divergences — the rule is
right, and by a much wider margin than the 53 D11 cites. Forcing the EOL order
onto the non-EOL path: 0 divergences. So the asymmetry is purely a performance
decision, and three things it says about that are wrong:

1. **The speed win is one pattern family, not the non-EOL path.** Across all six
   throughput cases, the EOL order is a tie or 1.5-4.1% FASTER on five of them.
   Only `[01]*1[01]{8}` loses, and it reproduces (156-159 -> 87-91 MB/s).
2. **The 43% is a gcc -O level artifact.** No gap at -O0, no gap at **-Os**
   (90.7 vs 91.7), gap at -O1/-O2/-O3. The decision stands — the harness builds
   at -O1, the bench at -O2 — but an embedder at -Os gets the slow number from
   both orders.
3. **The load-bearing premise was never written down.** Accept monotonicity: no
   state has plain accept 1 with a non-accepting EOL variant (verified over 6432
   patterns; it follows from clo_visit exploring a superset of edges in the same
   order). That is what makes "evaluate the accept once, at the landing
   position" sound. D11 argued "same state, same accept bit", which covers the
   positions a skip PASSES and says nothing about the one it LANDS on — the same
   shape of gap as the M2.12 ordering bug it was written to prevent.

**Coverage gap closed, with the critic's own claim corrected.** It reported that
NO .rxt case could catch removal of the reverse `pp + 1 < n` guard. Measured:
the pre-existing corpus catches 3, the new mid-pattern-`$` block catches 14, 17
across tests/base/. Overstated, not wrong in substance — on a family where `$`
always ends a branch, guard removal gives 0 divergences over 7.7M comparisons,
because no reverse skip state carries an EOL variant in that shape. The guard is
only load-bearing for a mid-pattern `$` with content after it, and the subject
has to be long enough for the skip to have somewhere to run.

**The process change worked, and it is the reusable result.** Four critics were
dispatched at these two targets across the session. The two told only to report
at the end delivered nothing, twice. The two required to append findings to a
file as they confirmed them delivered everything above. Build the mechanism
rather than repeating the instruction — the same conclusion R3's reflection drew
about tooling versus remembered principles, arrived at again from the other side.

Verification: 713 corpus + 42 CLI + 17 codegen + 5 trie-identity green; oracle
100% (705 cases); every new guard sabotage-validated with the exact edit
recorded.

## 2026-08-09 — the guards critic's second half: 13 more findings

The guards critic kept going after the batch already folded in, to 25 findings.
Thirteen new ones. The pattern is the same and worth stating once more plainly:
the compiler was not wrong anywhere. Every finding was about a guard being
weaker than its description, or a number I wrote being wrong.

**Three more places the "~14 in 500" error had propagated.** I fixed D16 and
nfa.c and thought I was done; it was also in `run_trie_identity.sh`'s own header
comment and in `tests/codegen/CLAUDE.md`, and plan.md still carried the old
"one positive control / 132 of 200" description. A wrong number copied into
four files is not four mistakes, it is one mistake with a propagation delay, and
the only reliable fix is to grep for it rather than to fix the place you
remember writing it.

**My .rxt header understated its own block, and contradicted its sibling.** The
header said the non-EOL sabotage "fails 3 cases of `[a-z].*|q$`". Measured over
the whole corpus: 11 — ten in this file (`[a-z].*|q$` 3, `a.*|b` 3, `=.*|;` 4)
and one in `tests/base/dot.rxt`. `tests/base/CLAUDE.md`, written in the same
commit, said 10. Two documents produced to record the same measurement,
disagreeing about it.

**And the gap I claimed was not empty.** "The forward half had no committed
case" is false: `dot.rxt`'s `.+` on "hello\nworld" already caught it. The R3.4
block is still a real improvement — 1 case to 11, and the EOL half genuinely had
nothing — but the claim was checkable by running the sabotage against the whole
corpus, which is precisely the operation that produced the numbers I quoted
next to it. I ran the sabotage against the two halves of one file and never
against everything else.

**A real gap, and it was hiding behind the file's own title.** `emit_dfa.c` has
the same post-skip accept rule twice, forty lines apart — forward
`last = pos`, reverse `sfound = pp`. This file covered the forward one ten times
and the reverse one ZERO times, while advertising itself as the home of D11's
coverage and containing a section literally headed "reverse-machine skip: the
match START must not be skipped past" that does not fire on the sabotage.
Disabling the reverse line fails 6 cases across tests/base (dot 2,
leftmost_semantics 2, quantifiers 2) and none here. Four patterns added
(`[a-z]*=`, `.*=`, `x.*y`, `[^\n]*=`); the file now catches it with 10.

**The bench case I added is a presence check, not a gate.** The critic graded
the regression instead of deleting the feature: capping the skip run at 8 bytes
discards 93% of the loop's reach on this subject and still measures 1.15-1.45x
ABOVE the 1000 MB/s budget. Only near-total deletion (3.1-4.1x) fails it — and
the case's own `grep rx_fs[0-9]+\[256\]` hard error already catches deletion for
free. So the budget adds approximately nothing over the grep. D12's sentence
applies to my own work: "a budget that cannot fail is documentation, not a
gate". [R3.9]. It also covers exactly one forward, non-accepting skip state; the
second table it emits is entered zero times, and its reverse skip table never
executes because the pattern cannot match — so reverse skip loops still have no
throughput coverage anywhere, which is awkward given M2.10/D13's negative result
rests on a suspicion about exactly that loop.

**A harness bug that is not mine but bites everything.** `run_bench.sh` samples
/proc/loadavg ONCE, before measuring, and that single reading decides LOADED for
the whole run. This box moved 1.94 -> 16.04 inside four minutes while critics
were working. A run starting at 5.9 against a limit of 6.0 is judged quiet and
then measures under a load of 13 — the critic watched a HEALTHY build median
575.5 MB/s on case (e) in such a window, a clean tree failing its own gate.
[R3.10]. This also explains the load swings I was working around all session.

**What held, and one thing worth keeping.** Case (e)'s 92% claim reproduces to
92.19% and its 1741.8 MB/s to a median of 1726.4 (spread 1.086x vs the recorded
1.081x). The `-Wall` check fires; the hard error fires; the EOL sabotage counts
are exact; `tests/bench/CLAUDE.md`'s prefilter/skip coverage table is right in
every cell; the self-reported EOL-skip-bound blind spot is accurate to the case
count. And the critic tried to break byte-identity the honest way — reversing
the order of provably-disjoint groups in trie_build, a change sound by the
code's own argument — and got 500/500 still identical. Subset construction plus
minimization absorbs it, so the "a correct change could produce
different-but-equivalent output" objection to D16 does not hold for that class.

One finding is recorded as NOT a finding, deliberately: the prefilter's
`last == -1` re-entry gate survives its own removal with zero corpus signal, and
the critic could not construct a witness. D3's accept-pruning means a machine
that has accepted cannot fall back to the pure start state, and every
empty-matching pattern checked emits no prefilter at all. Defensive, probably
unreachable — recorded so it is not re-attempted as a coverage hole.

Verification: 731 corpus + 42 CLI + 17 codegen + 5 trie-identity green; oracle
100% (723 cases).

## 2026-08-09 — D11 critic's final sections: a redundant premise, and a claim of mine that outran its measurement

The D11 critic closed out at 28.5 million oracle-checked comparisons across six
pattern families and four case alphabets, plus an ASan/UBSan pass with
exact-size subject buffers: zero divergences, zero sanitizer reports. It could
not break the shipped code. Two things came out of the last sections.

**A premise in emit_dfa.c that carries no weight, and says it does.** The
comment justified the EOL prefilter's validity on TWO conditions — bounded at
n-1 AND gated on `last == -1`. Only the first is load-bearing. The gate is
redundant given D3's priority pruning: the unanchored start self-loop is the
lowest-priority thread, so it is pruned out of every accepting state, an
accepting state's successors can never BE `fs`, and `last` is only ever set from
an accepting view — so `st == fs` already implies `last == -1`. Deleting the
gate produced 0 divergences over 8.0M comparisons and 0 corpus failures.

Two critics reached this independently from opposite directions: the guards
critic sabotaged the gate, found zero signal, and correctly declined to call it
a coverage hole; the D11 critic worked out WHY there is no signal and traced the
one shape that would break it if the invariant failed (`ab|a` on "axx"),
confirming from the emitted table that state 1's row is dead rather than `fs`.
The code is fine and stays as it is — the gate is free belt-and-braces. The
comment is fixed, because presenting a redundant condition and a load-bearing
one as a single claim is exactly how someone later simplifies away the wrong
half.

**And a claim of mine that outran its measurement, in the entry where I was
correcting someone else's.** My D11 addendum said the EOL order is "a tie or
SLIGHTLY FASTER" on five of six throughput cases at 1.5-4.1%. Those numbers were
taken at 1-min load 4.5-9.7 against tests/bench's own LOAD_LIMIT of 6.0, and the
critic flagged in its own hygiene note that it could not re-run them quiet (the
box hit load 26.7). 1.5-4.1% is inside the band where this box's load matters,
so the positive claim is SUGGESTIVE, not established. The negative — that the
EOL order is not materially slower there — IS established, and it is all the
correction needed. Softened in place.

That one stings in a useful way. I wrote it while cataloguing a critic's
load-contaminated numbers as "direction, not precision", and then stated my own
small deltas as fact in the same entry. The rule is not hard to remember; it is
hard to apply to the sentence you are currently writing.

**Also confirmed independently:** the corpus header's claim about the forward
skip bound is exact — relaxing n-1 to n fails 3 cases, in eol_engine.rxt (1) and
review_r2.rxt (2), and 0 in eol_scan_avoidance.rxt, precisely as the header
says. And the mid-pattern-`$` block added this session takes the reverse
`pp + 1 < n` guard from behaviourally unfalsifiable to 17 failing cases under
sabotage; the critic re-verified all of that file's expectations against PCRE2
directly rather than against python `re`.

Verification: 731 corpus + 42 CLI + 17 codegen + 5 trie-identity green.

## 2026-08-09 — strategy session: D18-D22, and a priority that should have been set at M0

Frank set direction that reframes several open gates. No code changed; five
decision entries and a plan restructuring. Recording the reasoning, not just the
conclusions, because the conclusions are cheap to restate and the reasoning is
what makes them applicable to the next question.

**The priority, stated explicitly for the first time (D18).** pcrec exists for
SPEED OF EXECUTION first and speed of COMPILATION second. Other regex libraries
offer other benefits; this one offers those. That single sentence resolves
trade-offs the earlier entries left drifting, and D12/D15's insistence on
measured budgets turns out to be downstream of it rather than a process
preference.

**Hyperspecialization, and the shape took three drafts to get right.** My first
version framed options as open/closed booleans. Wrong. The caller names a SET of
values per dimension and the product is over those sets; a singleton set is
fully specialized and compiled away INCLUDING when its element is not the
default. Asking for case-insensitive only is not "opening" case sensitivity — it
is hyperspecializing to the insensitive point, with no flag and no dispatch,
exactly as if sensitive-only had been asked for. Both are singletons; only the
specialized value differs. A dimension is an axis only at |set| >= 2.

**And every axis must EARN itself.** Before a dimension becomes a product axis,
measure whether specializing buys anything. It can fail three ways and all three
are wins: it folds into the front end, it is free at run time, or it is a pure
wrapper. Four predictions are recorded so results can be checked against them —
ASCII case-insensitivity folds to `bitmap |= swapcase(bitmap)`; encoding folds,
which APPROACH §4/§10 already commits to; streaming is NOT a wrapper and the
reverse pass is why; and anchoring is an axis that ALREADY EXISTS in the shipped
compiler and has never passed the test, since ENG_UNANCH/ENG_ATTEMPT split for
an implementation reason rather than a measured one. That last one is the
sharpest thing to come out of the discussion: D18's rule condemns something we
already ship, which makes DD-7 the first application of the principle rather
than cleanup.

**Execution side (D18).** Selection and execution are two steps: resolve the
engine once, execute it many times, so selection amortises. The selector is
itself generated and specialized — with case sensitivity as the only plural
dimension it is `if (ci) return engine1; else return engine2;`, not a registry.
Two properties are the whole point and both need structural tests: dispatch
resolves once per search call and never reaches the hot loop, and the
all-singleton case pays NOTHING — no dispatcher, no parameter, no indirection,
byte-for-byte what we emit today.

**The naming worry was smaller than I assumed, and measuring said so.** I was
about to write that multi-engine output needs everything namespaced. Checking
the emitter first: of 15 emitted identifiers, 12 are FUNCTION-LOCAL statics that
cannot collide across engines in separate functions. Only three are file-scope —
the `<prefix>_span` typedef and `<prefix>_search`'s declaration and definition.
So the work is emit the typedef once and share it, plus a distinct function name
per engine, which the named-entry-point scheme already supplies. The naming
answer and the API answer are the same answer. Worth noting the near-miss: I
nearly recorded a much larger problem from memory of how the emitter "must" work.

**Then D20 made even that mostly optional.** The product machinery is a separate
MODULE: an engine FINDER driving an engine GENERATOR that knows nothing about
dimensions and owes the layer above only naming constraints. Consequences: you
pay for the product only if you use it (D18's "all-singleton pays nothing"
becomes true by construction rather than by care); the CORE API never becomes
set-valued, since scalars are exactly right for something that compiles one
point, which deletes the API-change half of OS-0; and the finder can be built
much later or never. If the folding predictions hold it has no customer yet, and
that is a good outcome rather than a stalled one.

**D21 — optimization in waves, and the ORDER is the decision.** Algorithmic
first, then profiled code work, then compile time. Profiling a bad algorithm
optimizes the wrong loop, and optimizing compile time before execution speed
trades the primary goal for the secondary one. Research into other open-source
engines is explicitly part of the algorithmic wave and not a compromise. The
lead with the most obvious target: we use memchr only at exactly ONE escape byte
and otherwise fall to a bitmap, where ripgrep and Hyperscan choose the RAREST
byte by frequency — a different DECISION, not a faster implementation of ours —
and case (d) exists precisely because that bitmap path had no coverage.
memchr2/memchr3 covers the gap between our two paths and is probably the
cheapest real win available. Rejections get recorded with reasons.

**D22 — adversarial patterns are out of scope, and it cuts one way worth
stating.** pcrec compiles patterns a developer controls, ahead of time; it is
not a service taking untrusted regex, and contorting the design to survive an
attacker is not a goal. DD-2 drops to robustness. But the STACK budgets keep
their priority with a changed justification: DD-10/TS-4 is not attack hardening,
it is a legitimate deeply-nested pattern from a trusted source on a 128 KB musl
thread stack, which under D19 is an ordinary correctness bug for a threaded
caller. Written into the entry so nobody later reads "adversarial is out of
scope" and deletes the stack work as security theatre. The NFA/DFA caps also
stay exactly as they are — an attributable error was always the right answer for
an honestly-too-big pattern, never an anti-attack measure.

**D19 — thread-safety, audited rather than assumed, and both properties already
hold.** Usable FROM threads, never threaded: no worker pools, no parallel subset
construction. Generated code has 12 statics, all `const` with constant
initialisers, so load-time .rodata with no lazy init and nothing to race on; no
malloc, no errno, no locale, no non-reentrant libc; all working state
stack-local. The library has NO file-scope mutable state anywhere in src/, and
Ctx including its jmp_buf is a local of pcrec_compile so the longjmp path is
per-thread.

That audit also corrected R3: the review recorded "the generation counter is
file-scope while the marks are per-build arena memory". It is not — `gen` is a
member of `Marks` and `Marks marks` is a LOCAL of `pcrec_build_dfa`. The hazard
R3 described is real and handled; the scope claim was wrong. Had it been TRUE it
would have been exactly the thread-safety defect D19 is about, and I went
looking for that bug because a committed document said it was there. A wrong
description of correct code still costs, because the next reader reasons from
the description.

Guards rather than prose, because this is the invariant shape the project keeps
losing — true by construction, invisible to every test, killed by a plausible
one-liner (a memoisation cache, a hoisted scratch buffer, an errno-setting call,
a diagnostics counter, or under D18 a selector that caches its choice in a
global). TS-1 is the cheap one: assert every emitted static is const plus a
non-reentrant-symbol denylist, no gcc needed. The M4 landmine is captures — a
capture buffer is mutable per-search state and the tempting place to put it is a
static; it must be caller-provided or stack-local.

**Long-term vision (Beyond M7), recorded so the architecture is not painted into
a corner:** a PCRE2 compatibility layer, other-language usage libraries, a grep
CLI, and translators from other regex syntaxes. The last are FRONT-END modules
lowering into the existing AST — the shape APPROACH §3's parser extension points
already anticipate — which is what makes the direction affordable rather than a
rewrite. And the bindings are cheap for a reason that is easy to erode: the
generated code has ZERO runtime dependency on pcrec. Protect that deliberately.

**Working order agreed for the option work:** OS-0b (naming prep — cheap,
mechanical, blocks everything if left) -> OS-1 (case-insensitivity folding —
parser-only, no API work, the cheapest possible test of D18's own rule) -> the
finder only once a dimension has actually earned an axis. That ordering tests
the rule before building the machinery the rule implies.

No source changed this session; 731 corpus + 42 CLI + 17 codegen + 5
trie-identity remain green from the last verification.

## 2026-08-09 — OS-0b: multi-engine naming prep, and a test that can tell WHICH engine

First code since the D18-D22 strategy session, and the working order held: do
the cheap mechanical prep before anything needs it. The change is small in the
emitter and larger in the test, which is the correct ratio for this one.

**The emitter.** `emit_decls` did two unrelated jobs in one function — the
`<prefix>_span` typedef, which is FILE-scope and must be emitted once no matter
how many engines share the file, and the `<prefix>_search` declaration, which
is PER ENGINE. Split into `emit_span_typedef` and `emit_search_decl`, with
`emit_search_head` next to the latter so a declaration and its definition
cannot drift. The entry-point name now comes from `engine_entry_name()` and is
read nowhere else; the five sites that hardcoded `%s_search` (header decl,
inline decl, both engine definitions, the emitted `main`) consume it. That is
the whole seam a finder needs: hand each engine a different name and the
emitters never learn that options have a product (D20).

Output verified BYTE-IDENTICAL: 167 corpus patterns x 3 prefixes x 4 emission
modes (self-contained, paired .c, paired .h, --emit-main) = 1980 hashed
outputs, zero differences. A refactor that claims to change nothing should be
made to prove it rather than asked to be believed.

**The premise was checked, not assumed.** The plan line asserted that emitting
the typedef twice declares two distinct anonymous struct types and is an error
rather than a benign redefinition. It is: `error: conflicting types for
'rx_span'; have 'struct <anonymous>'`, under -std=gnu11 and -std=c99 both. Two
minutes to confirm, and it is now the thing the test asserts instead of a claim
in a comment. Same habit that paid off twice last session.

**A number in the plan was wrong, and it was wrong in my favour.** The OS-0b
line said run_codegen_tests.sh hardcodes "9 symbol patterns". It is 19 grep
sites across 11 generated files. Corrected in the plan line rather than left to
be re-derived by whoever reads it next.

**The test is the part worth describing.** All 19 sites now grep an engine BODY
extracted by entry name, not the whole file — with several engines,
`rx_fs[0-9]+\[256\]` is satisfied by any of them, so "this pattern emits a skip
table" quietly becomes "some engine in here does" without ever failing. But an
extractor is exactly the kind of thing that breaks silently, so it is not
trusted on inspection. The suite builds a two-engine file by applying the
transformation the finder will apply — one shared typedef, a distinct entry
name per engine, every other identifier untouched — and then requires a scoped
grep to find the skip table in the engine that has one ('.*=.*') and NOT in the
engine that does not ('^a|b'). A `body()` returning the whole file fails the
second check; one returning nothing fails the first. Neither failure mode can
pass by accident. That is the 4-and-8-branch-control lesson from the trie work
applied at the point of writing rather than after a critic finds the hole.

The fixture is also compiled under GENCFLAGS, which is what actually proves the
multi-engine output contract, and duplicating the typedef in it is asserted to
BREAK the build — the emit-once rule is a requirement with a demonstration
attached, not a tidiness preference.

**Five sabotages, each on a fresh tree with the edit asserted to have landed
before the tree was built** (MECH-2's lesson applied by hand; the helper is
scratchpad-only, since MECH-1/MECH-2 remain open and building them properly is
their own item). Exact edits and counts are in tests/codegen/CLAUDE.md. The one
worth repeating here: turning off `pick_skip_states` still fails the same 6
pre-existing checks it failed before the scoping change, which is the evidence
that scoping TIGHTENED coverage without weakening any of it. And isolating the
attribution step alone — `cp` instead of `body()` for engine B only — fails
exactly one check, so the new guard is load-bearing on its own rather than
riding on the fixture construction.

**What this does NOT do, stated so it is not mistaken for done.** pcrec still
emits exactly one engine per file; nothing generates two. The contract is
proven at the OUTPUT level (a file in that shape compiles and is greppable per
engine), not at the emitter level. Building the thing that emits several is
OS-0, and D20 deliberately leaves it unbuilt until a dimension has actually
earned an axis — which is OS-1's job next.

Verification: 731 corpus + 42 CLI + 22 codegen (the 17 pre-existing, unchanged,
+ 5 new) + 5 trie-identity green, ratchet clean, oracle 100% (723 cases). Box
was quiet throughout (1-min load 0.73-0.90); no performance claim is made here
and none is needed, since the emitted code is byte-identical.

## 2026-08-09 — OS-1: case-insensitivity folds, the prediction held, and two things it did not say

D18 wrote down four predictions specifically so results could be checked
against them instead of remembered favourably. This is the first one settled,
and the checking part turned out to matter: the headline prediction held
cleanly, and the two details around it were both wrong in ways worth keeping.

**The implementation is as small as predicted.** `cls_casefold` adds each ASCII
letter's other case to a class bitmap at parse time. NFA construction, subset
construction, byte equivalence classes, minimization and emission are untouched
and never learn the option exists. The API change is one scalar field
(`options.caseless`) plus `pcrec -i` — exactly the shape D20 argued for, since a
generator that compiles one point is correctly served by scalars.

The evidence that it is a FOLD rather than an engine: `-i 'aBc'` emits
byte-identical C to `'[aA][bB][cC]'`. Not equivalent, not similar — the same
bytes. There is nothing to dispatch between, so case does not become an axis,
and the ASCII half of DD-1 is now closed as a parser change.

**Measured against the design being rejected.** I built the runtime-checked
variant by transforming pcrec's own emitted C — same DFA, same emitter, same
gcc flags, with every subject byte routed through an `lc[]` table in the hot
loop — so the two differ only in WHERE case is handled. Folding wins on every
pattern that can be compared: 511.7 vs 458.9 MB/s on a keyword alternation
(spreads 505-520 and 453-463, no overlap), and 2650 vs 1964 on a pattern with
no letters at all. That last one is the useful control: it prices the `lc[]`
indirection alone at 26%, on a pattern where it can never change an answer.
`[a-z]+@[a-z]+` came in ~3% ahead with the ranges just touching — direction
established, magnitude not, and I am writing it that way this time rather than
after someone points at it.

The transform script refuses to emit a file it cannot justify: it counts the
rewritten sites and hard-errors on a memchr prefilter rather than quietly
comparing two different prefilters and calling the difference "case handling".
That refusal fired, which is how the next finding surfaced.

**Correction 1: the tables do not shrink.** D18 said byte-class merging "may
even SHRINK the tables". Almost never. Folding adds a letter's other case to an
existing class, so `ncls` is unchanged and the tables come out the same size —
192/192 entries on the keyword pattern, 12/12 on the class pattern. Shrinking
needs the pattern to already mention both cases: `aA` goes 9 entries to 6. True
but rare; "same size" is the honest expectation.

**Correction 2, and it is the biggest number in the whole exercise: folding a
leading letter destroys the memchr prefilter.** `hello` has one escape byte
from the start state; `-i hello` has two (`h` and `H`), so the emitter drops to
the bitmap loop. 2606 -> 1245 MB/s, a 52% loss. Nobody predicted it, and it is
larger than everything the comparison was set up to measure.

It does not change the verdict, and the reason is the part worth keeping: this
is a cost of CASELESSNESS, not of folding. A runtime-checked engine cannot use
memchr either — a single-byte search cannot see both cases — which is precisely
why that row has no runtime-checked variant to compare against. Both designs
pay it; only one of them also pays for the indirection. And it lands exactly on
D21's OPT-A lead: memchr2/memchr3 covers the two-escape-byte gap, and this is
now its second measured customer alongside case (d).

**The subtle half is the negation order, and nothing downstream can catch it.**
A negated class must be folded on the positive set and then complemented.
`[^a]` caseless is "neither a nor A"; fold after negating and you get every
byte. Both orders produce a case-CLOSED set, so no invariant, no structural
property, no equivalence check distinguishes them — only behaviour does. So it
is pinned twice: `n "A"` lines in tests/base/caseless.rxt, and a shape check
requiring `-i '[^a]'` to equal `'[^aA]'` AND to differ from `'[^A]'`. The
second half of that pair exists because the first alone would also pass if the
fold dropped a case instead of adding one.

**Where the fold is applied, and where it deliberately is not.** At the sites
that build a positive class set — `char_node` and `p_class`. NOT as a
post-parse AST walk, which is the tidier design and would cover future
constructs automatically: AST depth is unbounded in pattern length (a long
concatenation is a left-deep A_CAT chain), so that walk would add exactly the
recursion DD-10/TS-4 is trying to remove. Recorded in the code, because "why
didn't you just walk the AST" is a question this will attract.

**Test-format change.** `.rxt` blocks gained a `flags` directive (only `i`), and
both run.sh and verify_rxt.py honour it. The oracle maps it to
`re.IGNORECASE | re.ASCII` — the `re.ASCII` is load-bearing, since python's
IGNORECASE folds Unicode and would silently disagree with pcrec's ASCII-only
fold on exactly the cases a careless corpus would not cover. An unknown flag
letter is a hard error rather than a no-op; a silently dropped flag would
compile a different automaton and then verify the block against it.

Four sabotages recorded in tests/codegen/CLAUDE.md, each on a fresh tree with
the edit asserted to have landed. Worth noting the harness one: removing the
`-i` mapping from run.sh fails 21 of 56 caseless cases, which is what proves
the `flags` plumbing is real rather than decoratively present.

Verification: 787 corpus (+56) + 49 CLI (+7) + 28 codegen (+6) + 7 trie-identity
(500 patterns swept twice, case-sensitive and folded, 1000 comparisons all
byte-identical) green, ratchet clean, oracle 100% (779 cases). Measurements
taken with no critic running, load 0.59 before / 1.01 after, and reproduced in
a second run.

## 2026-08-09 — TS-1, and two boundaries added to a decision I had just committed

Two small pieces, one of which is a correction to my own work from an hour
earlier.

**D23 was stated more broadly than it is true, and Frank's question found it.**
The entry said ASCII case-insensitivity folds, full stop. It folds for the
CLASS-BASED tier, which is everything shipped — but two constructs defeat the
argument and neither was named. Backreferences: `(?i)(a)\1` compares captured
SUBJECT text against subject text, which is not a class-membership test, so
there is no bitmap to fold it into and a caseless backref needs a comparison at
MATCH time. That is the one place this dimension could still cost something at
run time, and where it would have to be re-examined against D18's rule. And
Unicode folding: ASCII folding is a bijection on 52 bytes so it is a bitmap OR,
while Unicode has one-to-many foldings (`ß` -> `ss`) and fold pairs of
different UTF-8 lengths — none of which is a bitmap operation, so DD-1 must
settle it on its own evidence rather than inheriting D23's.

Both are now in D23. Neither is shipped, so nothing is wrong in the code; what
was wrong was a decision entry that a future reader would have reasoned from.
That is the same failure mode as R3's "the generation counter is file-scope" —
a wrong description of correct work still costs, because the next person
reasons from the description rather than the code.

Also recorded there, because it came up and is worth knowing before M6: scoped
modifiers cost nothing extra. `(?i)`, `(?i:...)` and `(?-i)` fail cleanly today
with "requires module 'modifiers'", and when that module lands the fold does
not need redesigning — it is applied per-class at CONSTRUCTION time, so a
scoped flag just means "whichever setting is in effect where this class is
parsed": a parser state variable saved and restored at group boundaries, with
`options.caseless` as its initial value. The option and the inline syntax are
two spellings of one front-end change.

**TS-1 — the cheapest guard on the board, and its sabotage number is the
argument for it.** D19's property for generated code reduces to two mechanical
facts: every emitted `static` is `const` (so it is .rodata with a constant
initialiser — no lazy init, nothing to race on) and the output references no
non-reentrant or allocating libc. Both hold today by construction. The sweep
covers 18 emitted files across 9 emission shapes — both engines, EOL and
non-EOL, both prefilter kinds, skip states, the never-matches path,
case-folded, `--emit-main` — plus the paired headers, and the file count is
itself asserted so a sweep that quietly stops generating stops passing.

The number that justifies the whole thing: making every emitted table a
NON-CONST static fails 8 TS-1 checks and **zero** corpus cases. The code
compiles, matches identically, and passes the entire suite while being
thread-hostile. That is precisely the memoisation-cache and
hoisted-scratch-buffer failure mode D19 predicted, and under D18 it is also a
selector that caches its choice in a global. No gcc needed, ~60 lines.

One deliberate sharp edge, documented in place: the scan is textual and does
not strip C comments, so an emitted comment that merely mentions `malloc` will
trip it. Keeping it that way — a denylist that tolerates its own words in some
contexts is one nobody can reason about, and rewording a comment is cheaper
than the ambiguity.

Verification: 787 corpus + 49 CLI + 29 codegen (+1) + 7 trie-identity green,
ratchet clean.

## 2026-08-09 — the PCRE2 compliance survey, which found a miscompile and a missing guard

Frank asked for a compliance report against pcre2syntax.html. The report is in
docs/pcre2_compliance.md; what follows is what the exercise turned up, which
was more than a table.

**Method.** Two lesser-model subagents in parallel, both required to append to
a scratchpad file AS THEY CONFIRMED THINGS rather than report at the end (the
lesson from R3's four critics: the two that reported at the end delivered
nothing, twice). Both delivered — 33 sections of extracted PCRE2 syntax, and an
evidence-based probe of pcrec's actual accept/reject surface. Judgement calls
about feasibility stayed in the main session, since they depend on the D7
two-pass design and the M4 VM plan that a fresh agent does not hold. Aim
subagents at FACTS, keep the CLAIMS.

One unplanned bonus: the spec agent appended a `pcre2_dfa_match` compatibility
cross-reference from pcre2matching.html. PCRE2's own non-backtracking matcher
is exactly the right prior art for judging what pcrec can reach, and its
documented exclusion list (no backrefs, no recursion, no capture-conditionals,
no `\K`, only `(*FAIL)` of the control verbs) matched my independent
feasibility judgements almost row for row.

**Finding 1: `\v` was miscompiled, and the oracle agreed with the bug.** PCRE2
defines `\v` as vertical WHITESPACE. pcrec decoded it as vertical tab. Measured
against libpcre2 10.46: PCRE2 matches 0x0a 0x0b 0x0c 0x0d 0x85, pcrec matched
0x0b alone — six bytes against one, inside classes as well as outside.

It survived because python `re` ALSO reads `\v` as 0x0B, so
tests/base/escapes.rxt asserted the wrong answer and was oracle-VERIFIED wrong.
The tell was inside the parser: `\V` routed to module 'classes' while `\v` was
decoded as a control character — the same construct handled two different ways
ten lines apart. I checked every other escape against libpcre2 while I was
there; `\a \e \f \n \r \t` all agree exactly, so `\v` was the only one.

The generalisable lesson, now in upstream_issues.md: **where python `re` and
PCRE2 disagree on what a construct MEANS, a python-verified corpus certifies
the divergence instead of catching it.** The base tier is still the right first
oracle. It cannot be the last word on PCRE semantics, and this is a concrete
casualty in support of M7's differential work.

**Finding 2, the bigger one: the mandate's central guarantee had no test.**
"Unsupported constructs must fail with a clean 'requires module X' error, never
miscompile" is the project's core promise, and nothing checked it. It could not
live in the corpus — a `perr` block requires the PYTHON oracle to fail to
compile too, and python accepts `\d`, `\b`, `(?i)` and nearly everything else,
so every module-routed construct was untestable there. `# pcre2-only` does not
rescue it either: verify_rxt.py consults cur_skip only on m/n lines, never in
its perr branch. Nor could a perr block express the part that matters most —
that the diagnostic names the RIGHT module.

tests/reject/ now asserts per construct: exit exactly 1 (not 0, not a crash),
the expected module name, and no output file left behind. 85 constructs, plus
12 accept-controls so a parser that rejected everything could not score 100% —
the same control lesson the trie identity check learned the hard way — and a
floor on both counts so deleting coverage fails rather than shrinking quietly.

The sabotage that makes the case: reproducing the `\v` bug's exact shape on a
different escape (`\d` silently decoding to a literal `d`) fails 2 reject checks
and ZERO corpus and codegen checks. The bug class that just bit us was
invisible to everything else in the repo.

**Diagnostics fixed on the way.** Every one was already a clean rejection — none
was a miscompile — but several failed to name a module, telling the caller
their syntax was nonsense rather than what would implement it. `(*ACCEPT)`,
`(*SKIP)`, `(*CR)`, `(*script_run:...)` and every other `(*...)` reported
"quantifier does not follow a repeatable item", which is a correct rejection of
something that is not a quantifier; they now name module 'verbs'. `\K` and `\c`
and `\o` were "unknown escape"; they now name 'assertions' and 'misc'. `(?#`
was attributed to 'modifiers' rather than 'comments', `(?C` to 'modifiers'
rather than 'callouts', `(?&` to 'modifiers' rather than 'recursion', `(?|` to
'modifiers' rather than 'branch-reset'.

**On the report's own honesty.** The status vocabulary splits Frank's five
categories into seven, for two reasons the survey forced. Verified and believed
are different claims and this project has been burned by conflating them. And a
clean rejection is a DESIGNED state, not a gap — lumping it in with
non-compliance would misrepresent the majority of the surface. Every REJECTED
row is true only because tests/reject says so; the report says that explicitly,
so a row without a counterpart there is visibly an assertion rather than a
status.

Verification: 786 corpus (-1: the wrong `\v` block removed) + 49 CLI + 97
reject (new) + 29 codegen + 7 trie-identity green, ratchet clean, oracle 100%
(778 cases).

## 2026-08-09 — the survey's second divergence, found by the subagents' own reports

The two compliance subagents' closing reports arrived after I had already
committed the survey. Most of what they flagged I had found independently and
fixed in the same pass — the `(*...)` non-routing, `\K`/`\c` unattributed,
`(?&name)` misrouted to 'modifiers'. Three items were new, and one of them was
a second silent divergence.

**POSIX collating elements were accepted, and PCRE2 rejects them.** `[[.a.]]`
and `[[=a=]]` are collating-element and equivalence-class syntax. PCRE2 does
not implement them and errors out; pcrec compiled them into a class of literal
`[`, `.`, `a` characters. A pattern PCRE2 refuses, given a meaning PCRE2 never
assigns it — and python `re` accepts them too (with a FutureWarning), so the
base-tier oracle was blind again. Identical shape to `\v`, found the same way.

**The fix was worth slowing down for, and the reason is the interesting part.**
The obvious rule — "reject any `[.` inside a class" — is wrong and would have
broken working patterns. PCRE2 only treats `[.` as a collating opener when the
matching `.]` terminator actually appears later, so `[.a]`, `[.]`, `[[.]`,
`[a[.b]` and `[a.b.]` are ordinary classes that compile, and a leading `^`
suppresses the rule entirely because it sits between the bracket and the
delimiter (`[^.a.]` compiles). I probed 18 forms against libpcre2 before
writing a line of the fix; pcrec now agrees with PCRE2 on all 18.

Six of those are accept-controls in tests/reject rather than notes in a comment,
because **over-rejection is the opposite failure and just as wrong**. A naive
implementation would have passed every rejection row in the table while
silently breaking patterns that work today. That asymmetry is worth remembering
whenever a "reject it cleanly" fix goes in: the rejection is the easy half.

**Also closed: three accepted-but-untested gaps** the surface agent surfaced,
which is the section of its report I asked it to treat as most load-bearing and
which duly earned its place. `\a`, `\e` and `[\b]` (backspace inside a class,
which is a real PCRE rule) compiled correctly and had zero corpus coverage;
`a{}` as literal text and `[]]`/`[^]]` (a `]` first in a class is a member, not
a terminator) likewise. All now covered and oracle-verified. `\e` needed a
`# pcre2-only` marker: python `re` rejects it outright ("bad escape \e"), so it
was checked against libpcre2 directly — a third small instance of the same
theme.

**On the subagent method.** Both were told to write incrementally and both did;
both delivered complete files. What made the difference on quality, though, was
the division of labour rather than the count: the agents gathered FACTS (what
the spec says, what the binary does) and every judgement about feasibility
stayed in the main session, where the D7 two-pass design and the M4 VM plan
actually live. The one thing I did not anticipate was the spec agent adding a
`pcre2_dfa_match` compatibility cross-reference on its own initiative — PCRE2's
own non-backtracking matcher is the best available prior art for what pcrec can
reach, and its exclusion list matched my independent feasibility judgements
almost row for row.

Verification: 805 corpus (+19) + 49 CLI + 112 reject (+15) + 29 codegen + 7
trie-identity green, ratchet clean, oracle 100% (796 python-verified cases).

## 2026-08-09 — D24: the syntax construct registry, designed rather than built

Frank asked whether a single parse.c is the right long-term shape, given
PCRE2's flavours, options and "exists but only on certain engines" caveats. His
stated fear was the codebase that fills with `if python-compat do X else if
pcre2-dfa do Y else Z`, where every change cascades. Written up as D24 with
plan steps SR-1..SR-8; no code moved.

**The answer I gave, and the part I had to resist.** File size is not the
problem. parse.c is 467 lines and neither bug found today was caused by that,
nor would have been caught by splitting it. Saying so mattered more than the
proposal that followed — a refactor that looks like a fix for a problem it does
not address is worse than no refactor, because it spends the credibility you
would need for the real one.

The real defect is that one construct's identity lives in up to FIVE places:
esc_modules (10 rows), esc_char_value's switch (8 cases), the `(?X` chain (11
branches), the reject table (60 sites), the compliance report (90 rows). `\v`
was places 1 and 2 disagreeing ten lines apart with nothing enforcing
agreement. Uncomfortable follow-on: writing the reject table and the report
today MANUFACTURED two more copies, so I increased the duplication in the same
session that its cost became visible. The registry is as much a correction of
my own work as of the parser's.

**Frank's structural insight is the load-bearing one and the data backed it
harder than I expected.** He said syntax should drive, keep core syntax in
parse, farm the weird stuff to specialists, and that most weird stuff is a
variant of `\x` or `(?W)`. Checking the full inventory: every non-base
construct in PCRE2 enters through exactly FOUR doorways — after `\`, after
`(?`, after `(*`, and after `[[` inside a class — each decided by a single byte
or a name. The base tier reaches exactly one of them, once, for `(?:`.

That makes his performance principle — normal stuff fast, weird stuff can cost
lookups — true BY CONSTRUCTION rather than by optimisation: a 95% pattern does
zero registry lookups. SR-5 guards it with an instrumented build rather than
leaving it as a claim, because "true by construction and invisible to every
test" is the exact shape this project keeps losing.

**Four axes, kept apart, is the whole answer to the cascade fear.** Flavour
(which construct a byte MEANS), option (what it DENOTES), enablement (is it
available), engine (can it LOWER). The bloat comes from answering all four with
one mechanism. Give each its own and a flavour change merely REBINDS A ROW — it
cannot reach inside another construct's handler, because PCRE2's `\v` handler
and python's are different functions, not one function with a branch. That is
D18's hyperspecialization applied to the front end, which is the reassuring
part: it is the rule the project already committed to, not a new one.

**Where I pushed back.** Frank worried the registry would have to be dynamic or
we would be "compiling the compiler to compile regex". I split the concern: the
table stays `static const`, SELECTION is dynamic per compile. A runtime-mutable
registry buys nothing (handlers are C functions; a new construct means
rebuilding either way) and costs the thread-safety property D19 established and
TS-1 now guards — a mutable global registry is precisely the file-scope mutable
state that check forbids. Nice that a guard written this morning already earned
its keep by settling a design argument this evening.

**Where I soft-pushed to the tail.** Flavours themselves. The column exists
from SR-1; the machinery waits. D18's earn-its-axis rule applies verbatim — we
know of exactly ONE flavour-varying row (`\v`), so building selection for a set
of size one is the mistake OS-0 is deliberately not making. SR-7 is deferred by
design, the same way OS-0 is, and for the same reason.

**The thing I like most in the design is not mine.** Families as named masks
make `pcre2-dfa` a FAMILY — so PCRE2's own DFA exclusion list stops being prose
in my compliance report and becomes a definition the compiler can be pointed
at. The "only on certain engines" problem dissolves into the same mechanism as
flavours, and SR-8 becomes a column gaining teeth rather than a retrofit.

**Report fix, from Frank's review.** He noted the status column was
inconsistent — sometimes `REJECTED -> PLANNED`, sometimes the trajectory buried
in notes. Split into two columns: `status` (today, one value, greppable) and
`becomes` (intended end state, or `—`). 78 rows rewritten. Two statuses were
genuinely wrong rather than just badly formatted, and the split is what exposed
them: `\C` was labelled `PLANNED` when it is REJECTED today, and `[x&&y]` was
labelled `PLANNED` when pcrec already agrees with default PCRE2 (both accept it
as a literal class; the set-operator reading needs a PCRE2 option we do not
model). Added `AGREES-REJECT` for constructs where PCRE2 refuses too and
matching it IS compliance — the POSIX collating row was misrepresented as a
divergence when the divergence is now fixed and agreement is the current state.
Those columns are deliberately the prototype of the registry's own fields.

## 2026-08-09 — session close

Six commits, all pushed (`13e649b..a23d4be`). Working tree clean apart from the
uncommitted docs/wake.md hand-off. Nothing left in `STATE:started`, so there is
no half-finished work to reconstruct.

Landed: **OS-0b** (multi-engine naming prep, engine-scoped codegen greps),
**OS-1/D23** (ASCII case-insensitivity folds — the first of D18's four
predictions settled, and it held), **TS-1** (no mutable statics, no
non-reentrant libc in generated code), **PC-1** (the PCRE2 compliance survey),
and **D24 + SR-1..SR-8** (the syntax construct registry, designed not built).

Two real bugs found and fixed, both silent, both by reading the PCRE2 syntax
reference against the parser rather than by any test: `\v` decoded as vertical
tab when PCRE2 means vertical whitespace, and POSIX collating elements accepted
when PCRE2 rejects them. Both survived because python `re` agreed with pcrec,
which is the session's most transferable finding — the base-tier oracle
certifies flavour divergences instead of catching them.

Test surface grew from 731 corpus + 42 CLI + 17 codegen + 5 trie-identity to
805 corpus + 49 CLI + 112 reject + 29 codegen + 7 trie-identity, with
tests/reject/ as a new directory guarding the "never miscompile" mandate that
previously had no coverage at all.

**Next session: SR-1**, the construct table. It is the step that pays for
itself immediately — it collapses the five-way duplication that produced `\v`
— and D24 records the reasoning so it does not need re-deriving. Read D24
before starting; the four-doorway argument is what makes the design small, and
the four-axes table is what keeps it from becoming the `if flavour else if
flavour` cascade Frank was right to worry about.

## 2026-08-09 — SR-1: the syntax construct registry, built

Baseline verified green before touching anything, and it matched the hand-off
brief exactly: 805 corpus / 49 CLI / 112 reject / 29 codegen / 7 trie-identity,
verify_rxt 796/796, fuzz seed 1 with zero divergences, `make bench` with zero
budget failures (linearity ratio 4.06). Worth saying plainly because the brief
asked for it as a stop condition: nothing about this environment differs.

**What landed.** `src/parse/registry.c` — 67 rows describing every non-base
construct as `static const` data: 39 escapes, 24 `(?X` groups, 1 verb catch-all,
3 class brackets. The row vocabulary (RegRow, FEAT_/FLAV_/ENGM_ masks,
RS_/RD_/RF_ enums) lives in core/internal.h, which is also what makes rebuilds
correct — the Makefile's object rule already depends on that header, and a
separate registry.h would have been invisible to it.

**parse.c is untouched.** SR-1 is the table; SR-2 is the dispatch. So this
commit cannot change behaviour, and the 805-case corpus passing is a
consistency check rather than evidence. The evidence that matters is the new
tests/registry/ check.

**The table alone would have been a sixth copy, not a fix.** That is the thing
worth remembering from this step. Five scattered descriptions of each construct
is what produced `\v`; adding a sixth — the newest, therefore the first to
drift — improves nothing by itself. So SR-1 shipped with the conformance check
rather than deferring it, and the check asserts in BOTH directions:

- **table → parser**: every row's own `syntax` field is compiled for real and
  the diagnostic must match EXACTLY. Substring matching would let a row name
  the wrong module and pass.
- **parser → table**: a 255-byte sweep of each doorway. If the parser says
  "requires module" for a byte, a row must exist and name the same module.
  **This is the direction that catches a construct added to parse.c with no
  row**, which is precisely the `\v` drift, and direction one is structurally
  blind to it. The sweep reports what it covered: 39 bytes routed after `\`,
  38 inside a class (one fewer — `\b` is backspace there), 254 after `(?`.

Probes come from each row's `syntax` field, so a new row covers itself with no
test edit. That is safe here and would not be in tests/reject/: this is a
conformance check between two descriptions, asserting they AGREE, never that
the rejection is correct. The moment a check asserts correctness it must not
share a source with what it checks — the trie-identity lesson, and why SR-4
keeps the accept-controls hand-written.

**Sabotage-validated, five edits, all caught** (exact edits, not just counts,
per the house rule; each reverted after measuring):

| edit to src/parse/registry.c | failures |
|---|---|
| `\v` row's module `"classes"` → `"assertions"` | 4 |
| delete the `\K` row entirely | 2 (both sweeps) |
| insert a row for `\n`, a BASE escape the parser compiles | 4 |
| collating message → "POSIX collating elements are unsupported" | 2 |
| drop `RF_CLASS_BASE` from the `\b` row | 2 |

The `\n` sabotage is the one I would keep: it is the only one that tests the
boundary the design rests on, that the table describes NON-BASE syntax and the
base tier never consults it.

**A real bug in the check, found by sabotaging it rather than by writing it.**
The S2 run reported two failures but printed only one, because `bad()` writes
to unbuffered stderr while PASS lines sit in a block-buffered stdout pipe, so a
PASS and a FAIL spliced into one line and stopped matching a line-anchored
grep. Fixed with `fflush(stdout)`. Nothing was wrong with the assertions; the
REPORTING was lossy, which is the failure mode that makes a test lie quietly.

**Two departures from SR-1's plan text**, both now under D24 as "SR-1 as built":
no [256] index (a linear scan over rows the base tier never reaches — an index
would be an unmeasured axis, and in C would need either a hand-maintained
parallel array, i.e. a second home for the selector bytes, or an X-macro used
nowhere else), and no handler field until SR-2 determines its four signatures.

**One thing the design needed that D24 did not name:** a third status. The plan
had "handler or NULL" carrying the whole meaning, but POSIX collating elements
are not awaiting a module — PCRE2 rejects them too, so agreement IS compliance
and there is no module to name. `RS_REJECTED` is now distinct from `RS_MODULE`,
which also matches the `AGREES-REJECT` status the compliance report grew for
the same constructs on the same day. The two documents converging on the same
distinction independently is mild evidence it is a real one.

**The `engines` column is recorded design intent, not measurement**, and the
file says so in its header. Nothing consumes it until SR-8/M4. It is the one
part of this table a future reader could mistake for established fact, so it is
labelled in the data, in src/parse/CLAUDE.md and here. When the VM lands, treat
those values as claims to check, not as a spec.

**Next: SR-2** — route the four doorways in parse.c through the table and
shrink parse.c to the base grammar. Its acceptance bar is byte-identical
emitted output across the corpus, proved the way OS-0b proved it (167 patterns
x 3 prefixes x 4 emission modes = 1980 hashed outputs; the script pattern is in
that session's entry). tests/registry/ was built to be SR-2's safety net as
much as SR-1's: it already pins every diagnostic string SR-2 must reproduce.

## 2026-08-09 — R4: adversarial review of SR-1, and what it cost me

Frank asked whether SR-1 had had a critic pass. It had not — R1–R3 covered
earlier checkpoints, and a design conceived (D24) and built (SR-1) on the same
day had faced nobody. D6 requires a panel at every major checkpoint, so this was
a straightforward process miss, and the pass paid for itself within the hour.

Three critics, deliberately different lenses, all required to write findings
incrementally (the R3 lesson holds: batching critics deliver nothing). Compiled
review: docs/reviews/2026-08-09-sr1-registry.md. Twelve findings; eight fixed,
two recorded as forward work, two rebutted in part.

**The finding that matters.** Nine rows — `\1`..`\9` — documented "octal escape
if no such group". PCRE2 10.46 raises error 115 "reference to non-existent
subpattern" unconditionally; the octal fallback is Perl/PCRE1 and does not
survive into PCRE2. I re-measured it myself against libpcre2 before accepting
the finding, and the critic was right. So the file built to be the ONE TRUE HOME
for PCRE2 semantics shipped with nine rows asserting a false one, on day one,
because I wrote the notes from memory instead of checking. The wake brief's
"measure before describing" was on the screen when I did it.

That is the fifth consecutive checkpoint where reading a spec against pcrec beat
running pcrec: ~54M oracle-checked comparisons across five checkpoints have
found zero compiler defects, while afternoons of reading PCRE2's syntax
reference have now found three real errors. The registry exists BECAUSE of that
pattern and immediately demonstrated it.

**Two of the three worst findings were in the TEST, not the artifact.** Deleting
both collating rows was 100% invisible — 116/116 green. Not the empty-kind check
(the POSIX row survived), not the coverage floor (65 >= 60), not table->parser
(it iterates rows that EXIST, so absence is unobservable), not even the two
hand-written `[.a.]` probes, because those exercise the parser rather than table
membership. The registry could silently lose its record of the very incident it
was built to prevent. And the sweep — the direction I called "the whole point"
in three separate documents — covered two of the four doorways. VERB and
CLASSBRACKET were never swept at all.

Both now fixed: all four doorways swept, fixed-text rows checked against their
exact message (the class-bracket sweep validated 1 of 3 rows until I noticed the
"requires module" marker excluded them), and a hand-written required-rows
manifest that catches deletion. Sabotage battery grown from five edits to seven;
the two new ones were invisible before. 116 -> 126 checks.

The critic's framing of the floor is the keeper: *a floor answers "did someone
delete a lot", never "did someone delete the right ones"*, and no floor loose
enough to tolerate ordinary churn can catch a two-row deletion. The fix is a
manifest, not a tighter number.

**A wrong citation I had already propagated.** D24 justified rejecting a mutable
registry with "the thread-safety property TS-1 guards". TS-1 scans EMITTED
OUTPUT only; it would not see a mutable global in src/. The honest guard is
D19's compiler-side property, which D19 itself records as audited by hand and
mechanized by nothing. The conclusion was right, the cited guarantee did not
exist, and I had already copied it into registry.c and internal.h. Corrected in
all three. Exactly the shape of D19's own correction to R3 — a wrong description
of correct code, which the next reader reasons from. The cost of a bad citation
scales with how quotable it is.

**Verifying the mitigation beat finding the hole.** The tests critic proved the
probe-from-syntax circularity is real (the same wrong module in BOTH parse.c and
registry.c passes 116/116), then ran tests/reject/ against its own sabotage and
found that IT catches the case, because its 93 expectations are hand-written
literals. That turned "the check is circular" from an alarm into a precise
statement of residual risk: a NEW construct, wrong in both files, with no
reject-table row, is caught by nothing. Brief future critics to attack the
defence, not just the target.

**Frank's macro suggestion turned out to be a correctness fix.** He asked for
the row details behind a light abstraction. The `M_<module>` macros emit the
feature bit and the diagnostic name as a PAIR — which closed a critic finding
that the feature mask's VALUE was never checked, only its zeroness, and made an
invented module name a compile error (verified: `M_wrongmodule` undeclared,
build fails). A readability change that independently killed a HIGH finding's
attack path.

**Also recorded:** K2 in known_issues.md (pcrec prints "(backreference/octal)"
for `\1`..`\9`, describing PCRE2 behaviour that does not exist — cosmetic today,
wrong advice once module 'backrefs' lands, deliberately NOT fixed because SR-2's
bar is byte-identical output). The `engines` column now states why it disagrees
with PCRE2's own DFA: pcre2_dfa_match supports lookaround, atomic groups and
recursion because it is a breadth-first bytecode simulation, not a classical
automaton like ours. plan.md corrected in four places, including SR-6's claim
that rows "already name the handler" (they do not) and the deeper gap it hides:
no status value means "implemented by module X", so SR-6 carries an unwritten
schema change.

**Still open, deliberately.** `pcrec_registry_find` takes no flavour argument,
so SR-1's "short chain for the rare flavour-varying byte" is not expressible in
the shipped shape — recorded on SR-7 as a signature change, not fixed, since a
duplicate selector fails loudly today. And the "sixth copy" objection stands as
strategy: the answer is to do SR-2, not to argue.

**Next: SR-2**, unchanged. Its acceptance bar is byte-identical emitted output
across the corpus (167 patterns x 3 prefixes x 4 modes = 1980 hashed outputs),
and tests/registry/ now pins 126 checks worth of the diagnostics it must
reproduce.

### R4 addendum — two findings I under-triaged on the first pass

The tests critic's final report landed after I had already committed the R4
fixes, and two of its items deserved more than I gave them.

**E1, which I had waved off as closed-by-construction.** A row carrying
FEAT_CLASSES while printing "assertions" passed 116/116. I claimed the M_<module>
macros closed it, and they do — for macro-built rows. A row written LONGHAND
still mismatches silently, and "correct by construction" with nothing testing it
is the precise shape of claim this project keeps losing. Now tested, without
introducing an external module list (which would be another second home):
across the table, feature mask and module name must be a BIJECTION, so a single
mismatched row necessarily collides both with rows using its mask and with rows
using its name. Validated by reproducing the critic's exact edit in longhand
form — 4+ failures naming the colliding rows. 126 -> 127 checks.

**The verb sweep is weaker than "all four doorways swept" implies, and I said
that sentence to Frank without qualifying it.** `(*...)` is decided by a NAME;
my sweep probes one byte after `(*`. It proves every single byte reaches the
catch-all, and proves nothing about a name-conditional branch — which is exactly
what the critic added to parse.c to defeat it. Not fixable without per-verb
rows, which belong to module 'verbs' (SR-6). Recorded as a named limitation in
the test, in tests/registry/CLAUDE.md and in the review, because an unqualified
"swept" reads as coverage it does not have.

Both are in the review as F13 and F14. The lesson worth keeping is narrower than
either finding: BOTH were cases where I accepted a structural argument ("the
macro makes it impossible", "the doorway is swept") in place of a test, having
spent the whole day arguing that this project loses exactly those.

## 2026-08-09 — session close (SR-1 + R4)

Five commits, `25a2383..092f08c`, all pushed. Working tree clean apart from the
uncommitted docs/wake.md hand-off. Nothing in `STATE:started`, so there is no
half-finished work to reconstruct.

**Landed:** SR-1 (the syntax construct registry — 67 rows, one declarative home
per non-base construct), its conformance check (tests/registry/, 127 checks,
eight sabotage validations), the M_<module> row-shape macros, and R4, the first
adversarial panel over any of it.

**Baseline at session start matched the hand-off brief exactly** and is
unchanged at close except where deliberately grown: 805 corpus / 49 CLI / 112
reject / **127 registry (new)** / 29 codegen / 7 trie-identity, verify_rxt
796/796, fuzz seed 1 zero divergences, `make bench` zero budget failures.
Verified from a fresh `git clone` three times during the session.

**The session in one line:** the registry was built to stop PCRE2 knowledge from
drifting, and within hours it had itself drifted — nine rows asserting a PCRE2
semantic that does not exist — which is the strongest argument for the thing it
is, and the strongest argument for running the panel before believing any of it.

**What I would tell the next session about my own errors**, since they were all
the same error:

1. Nine rows written from MEMORY (`\1`..`\9` "octal escape if no such group";
   PCRE2 raises error 115 unconditionally). The wake brief said "measure before
   describing" and I did not.
2. A test whose documentation described what it was MEANT to do — the sweep
   covered two of four doorways while three documents claimed four.
3. Two findings I argued away structurally ("the macro makes it impossible",
   "the doorway is swept") instead of testing, on the very day I spent arguing
   that this project loses exactly those claims.

All three are the same failure: asserting instead of measuring, in a session
whose entire subject was the cost of asserting instead of measuring.

**What went right and is worth repeating.** Writing the conformance test BEFORE
the macro refactor meant a 331-line restructure was proved behaviour-identical
for free. Dispatching three critics with deliberately different lenses caught
things no single lens would have. Requiring incremental writes worked again —
all three delivered, and the one that batched its final summary had already
banked everything in its file. And the tests critic ran the SUITE against its
own sabotage rather than just its target, which is what turned "circular" from
an alarm into a precise residual risk. Brief future critics to attack the
defence, not just the artifact.

**Frank's steer this session:** do not early-optimise the registry lookup (a
linear scan over rows the base tier never reaches, 33.6 ns against a 90 us
compile floor), and hide the row details behind a light abstraction. The second
turned out to be a correctness fix, not a cosmetic one — the M_<module> macros
pair each feature bit with its diagnostic name and make an invented module a
compile error.

## 2026-08-10 — SR-2: the registry stops being a sixth copy

parse.c is the base grammar and nothing else now. Every non-base construct
leaves it through one of four calls in the new `src/parse/ext.c` — after `\`,
after `(?`, after `(*`, after `[` inside a class — and registry.c answers.
`esc_modules[]`, the `(?X` ternary chain, the `(*` catch and `reject_collating`
are gone from parse.c; the file lost 90 lines and, more to the point, lost the
property of growing whenever a construct is added.

**The acceptance bar, met: 4173 hashed emission cases, zero differences.** The
baseline is a pristine `git archive HEAD` build rather than "the binary I had
before I started", which is the only version of that sentence worth trusting.
Wider than OS-0b's 1980: the corpus (179 patterns x 3 prefixes x 3 modes, plus
`-i` and `-e utf8`), a 255-byte sweep across eight doorway contexts, and
tests/reject/'s own strings — which set A misses entirely, because they live in
a `.sh` and not in any `.rxt`. Each case hashes stdout, stderr, exit status,
the paired `.c` AND the `.h`. A restructure that reroutes REJECTION paths has to
be proved on rejections, and OS-0b's proof only covered emitted C.

**Then the sabotage battery found something the proof could not.** Seven edits,
each on a fresh tree. Six were detected (20 to 192 cases each; one fails the
build, which counts). The seventh — deleting the `at_class_open` guard I had
just written — changed 0 of 4173 cases and broke no test in the suite.

An invisible branch is a question, not a conclusion, so I went looking for what
sat behind it, and it was a real bug: **pcrec accepts `[:alpha:]`; PCRE2 rejects
it** ("POSIX named classes are supported only within a class"). Measured against
libpcre2 10.46 across twelve probes: at a class's own opening bracket, `:`
behaves exactly like `.` and `=` — delimiter-pair, conditional on a later `:]`,
suppressed by `^`. pcrec has RF_CLASS_DELIM rows for two of the three
delimiters. Recorded as K3, NOT fixed here, because SR-2's whole claim is
byte-identity and a behaviour change would dissolve it.

**Third time this exact shape has appeared** — after `\v` and the collating
elements — and the third time python `re`, the base-tier oracle, accepted the
divergence rather than catching it. The corpus is structurally incapable of
finding this class of bug. Only libpcre2 or reading the spec can.

**Two departures from the plan text, both recorded in D24.** The handler field
is deferred AGAIN, and the reason inverted: SR-1 deferred it because its type
was a guess, and ext.c has now fixed all four signatures — but every row is
RS_MODULE or RS_REJECTED, so every handler would be NULL and the branch calling
one would be dead code no test can reach. That is precisely the shape R4's F13
and F14 both turned out to be. SR-6 gets the field with a customer attached, at
no extra cost. And `RF_CLASS_DELIM` joined the schema, because the collating
elements' recognition rule is the construct's, not the base grammar's, and
leaving it behind would have half-moved the doorway.

**My own tooling failed twice, in the way this project's docs keep warning
about.** The first sabotage script checked its edit with `grep -F` on a
multi-line pattern — which greps each LINE independently, so a successfully
removed block still "matched" via a stray `}`. And an empty replacement string
made the post-edit guard vacuously true while the editor had already failed, so
two sabotages that never applied reported "0 cases differ" — indistinguishable
from "the test cannot detect this". MECH-2 exists in the plan because of exactly
this failure a session ago, and I rebuilt it rather than reaching for it. Both
guards now live in one language, as exact substring tests, and abort with no
number rather than printing a reassuring zero.

The lesson worth generalising is narrower than "write sabotage tests", which I
already believed: **after a change, ask which of the branches you just added no
test can see.** The byte-identity proof was the deliverable; the question about
its blind spot was what found the bug.

Baseline unchanged and green: 805 corpus / 49 CLI / 112 reject / 127 registry /
29 codegen / 7 trie-identity, fuzz seed 1 zero divergences.

## 2026-08-10 — SR-3, SR-4, and R5: the arc lands, and the panel finds four bugs

Three commits after SR-2: `--list-syntax`/`--explain` (SR-3), the dump made
load-bearing (SR-4), and the R5 fixes. Suite grew 805/49/112/127/29/7 ->
805/73/192/127/29/7, all green, plus two SR-4 doc checks.

**SR-3** renders the 67 rows as 12-column TSV and answers for one construct
through the same helpers, so the two cannot disagree. Twelve columns, not the
plan's seven: SR-4 needs to know how to PROBE a row and what text to expect, and
deriving those from the rest would put ext.c's diagnostic templates in a second
home. Kept INTERNAL rather than public API — the CLI includes core/internal.h
for two functions returning finished text. Promoting into lib/pcrec.h later is
the reversible direction; the reverse is not.

**SR-4 did not do what its plan line said, deliberately.** The text says
tests/reject/ should iterate the dump INSTEAD of its 93 hand-written entries.
That trade gives away the property it is protecting: since SR-2 the module names
live in ONE place and the parser renders from it, so a test reading the same
table cannot see a WRONG name. I did not argue this — I measured it on sabotaged
trees:

    \d's row classes -> misc            hand-written 2 fail, iterated 0
    \s's syntax -> "zz" (not a probe)   hand-written 0,      iterated 1 fail
    the dump returns empty              the vacuity guard fires
    a NEW row, wrong module, no hand-written entry     caught by NEITHER

So iteration was ADDED (66 checks) and the hand-written rows KEPT. The last line
is the honest limit and it is in the plan and the CLAUDE.md: **SR-4 did not close
R4's residual circularity.** The only external source of truth for those rows is
libpcre2, which is now PC-3.

pcre2_compliance.md is NOT rendered wholesale. Doing that would replace a survey
— DFA-feasibility judgements, PLANNED vs PLANNED-HARD reasoning, the divergence
post-mortems, every row about BASE syntax — with an inventory the registry can
already print. A generated construct index is spliced between markers, and two
checks hold the seam. The `--names` one catches the realistic failure: a module
renamed in registry.c leaving the prose describing something that no longer
exists.

**R5: three critics, three lenses, four confirmed bugs — none of them mine.**

K3 grew a second half and K4, K5, K6 are new. Two are MISCOMPILES of exactly the
class the charter forbids: `a{65536}` and `{1}` both silently become literal
text and compile a matcher for a different language. The other two are the
class-bracket doorway getting PCRE2's delimiter-pair rule wrong in both
directions. All four are pre-existing; none is an SR-2/3/4 regression. Two
critics converged independently on the class-bracket pair, which is the
strongest signal in the review.

**SR-2's byte-identity claim held under a better instrument than mine.** The
behaviour critic built its own driver, PROVED ITS SENSITIVITY FIRST (it catches
the at_class_open sabotage my 4173-case harness could not), enumerated eight
classes my harness structurally could not reach, and closed them with 8790
further cases. Zero differences. That is how a claim should be checked.

**Two findings were against my own work, and both were the same shape as the
bugs.** I documented SR-2's `noreturn` attributes in three places as a forcing
function that "fails the build". It warns. There is no -Werror and no -W option
controls that warning. And my sweep header claimed "every byte 0x01..0xff" while
`b="$(printf ...)"` silently made byte 0x0A the empty string — eight cases
testing a shorter pattern and reporting as passes, on the byte most likely to
behave specially in a regex parser. Reworded the first; closed the second with
240 byte-exact python-driven cases across ten doorway contexts (zero
differences), so the claim is now true rather than merely corrected.

**The question that actually found things**, and it was not on any checklist:
*which of the branches I just added can no test see?* I asked it because a
sabotage returned zero, and K3 was sitting behind the answer. Every other bug in
R5 came from pointing the same question at something else — at the accept
controls (all seven put the class at the end of the pattern, which is why K4
survived), at the ratchet (empty, and structurally unable to hold any of these),
at the drift detector (whose remedy regenerates the sabotage).

**An identity proof cannot see a bug that both sides share.** SR-2's proof was
correct and reported "no change" for K4 because K4 was carried across
faithfully. It answers "did I change anything", never "was it right to begin
with". This session needed both instruments and only had one until the critics
brought the other.

**My tooling failed three times, all with one signature: a check that reports
success when it has not run.** A multi-line `grep -F` guard (grep splits the
pattern per line, so a removed block still "matched" via a stray `}`); an empty
replacement making a post-edit guard vacuously true while the editor had already
failed; and the newline strip above. MECH-1/MECH-2 have been in the plan for two
sessions for precisely this, and I hand-rolled the machinery again instead of
building them. That is now the highest-value process item by a distance.

**Left for next time, in order:** K5 and K6 (the miscompiles), then K3+K4 (one
fix, but it needs a D24 schema call on whether class-open becomes a fifth
doorway kind), then MECH-1. R5-Q1 — whether to adopt -Werror — is Frank's.

### Session close — 2026-08-10

Five commits, `cc125b6..5a0a9e7`, **NOT pushed** (the previous session ended
pushed; this one was not asked to). Working tree clean apart from the
uncommitted docs/wake.md hand-off, which is now in .gitignore because I staged
it twice with `git add -A` after a brief that warned about exactly that in prose.

**Landed:** SR-2, SR-3, SR-4, and R5 — the first adversarial panel over all
three. The SR arc's point is delivered: parse.c is the base grammar and nothing
else, and adding a construct means adding a row.

**Baseline at close, all green from a fresh clone as well as in place:** 805
corpus / 73 CLI / 192 reject / 127 registry + 2 SR-4 doc checks / 29 codegen /
7 trie-identity, verify_rxt 796/796, fuzz seed 1 zero divergences, bench zero
budget failures at load 1.5.

**The session in one line:** three steps of pure restructuring, proved
behaviour-identical on 4173 cases — and the four real bugs were all found by
asking what the proof could not see.

**What I would tell the next session about my own errors.** They were not the
same error this time; they were the same SIGNATURE, three times, and all in
tooling rather than code: a check that reports success when it has not run.
Multi-line `grep -F` (greps each line independently, so a removed block still
"matched"). An empty replacement string making a post-edit guard vacuously true
while the editor had already failed. `$(printf ...)` stripping the trailing
newline so byte 0x0A became the empty string, and eight sweep cases tested a
shorter pattern and passed. MECH-1 and MECH-2 have been in the plan for two
sessions to prevent precisely this and I hand-rolled the machinery again.

**What went right and is worth repeating.** Capturing the baseline from a
pristine `git archive HEAD` build rather than "the binary I had before I
started". Requiring critics to write findings incrementally — six for six over
two sessions. Briefing them to attack the DEFENCE: two independently converged
on the class-bracket bugs, one disproved a claim in my own comments, and one
predicted a sabotage result would be stale, measured it, and reported that it
was wrong. And when a design decision cut against the plan text (SR-4's
"instead of"), measuring both options on sabotaged trees rather than arguing —
2 failures vs 0 settled it in a way no amount of reasoning would have.

**Next:** K5 and K6, the two miscompiles. Then K3+K4, which need a D24 call on
whether the class-open position becomes a fifth doorway kind. Then MECH-1.
R5-Q1 (-Werror) and the push are Frank's.

### R5 addendum — the critics' later findings, and a claim of mine they corrected

Both remaining critics finished after I had already written the session close,
and their later sections deserved more than the triage I had given them.

**The `at_class_open` framing in SR-2's commit message is wrong, and the
behaviour critic proved it.** I wrote that deleting the guard "changes 0 of 4173
cases and breaks no test", and called it an invisible branch. The second half is
true of the repo's tests; the first half is a property of MY HARNESS. Five
one-line patterns expose it — any class whose first member is `:`. The critic
then verified WHY nothing saw them instead of guessing: no corpus pattern opens
a class with `:`, the reject suite's only `[:` row is `[[:alpha:]]`, and
registry_check's sweep template is `"[[%ca%c]]"`. Every probe of that doorway in
the entire repo puts a literal `[` between the class bracket and the delimiter,
so all of them test 4b and none tests 4a — which is exactly the distinction the
argument encodes.

Closed with `accept '[:]'` and `accept '[:a]'`, both accepted by libpcre2 too.
Deliberately not `[::]` or `[:a:]`, which PCRE2 rejects and pcrec wrongly
accepts (K3) — pinning those would cement the bug. The sabotage that was
undetected now fails 2 checks.

**And the pure-restructure claim held against 137,378 more cases** than I ran:
97,818 EXHAUSTIVE short strings (every string of length <=3 over a 30-byte
metacharacter alphabet, so no human chose what to try) and 30,770 structural
ones — the paren cap straddled at 245..255 with a doorway inside the nest, a
delimiter pair whose closer sits 20000 bytes from its opener, real verb NAMES
(the first name-level probe of a doorway everything else tests byte-wise), real
.c/.h files diffed on disk, raw newlines and high bytes. Zero differences.

**One latent trap in my own shape, now fixed.** `pcrec_ext_class_bracket`
returned `bool` and no path could produce `true`, while both callers discarded
it. That is a worse lie than the noreturns are honest about: when SR-6 gives a
class-bracket row a handler meaning "consumed, carry on", both callers would
ignore it and fall through to member parsing with nothing objecting — in the
doorway with the weakest coverage. Now `void`, so adding a value forces both
call sites to be read.

Byte-identity re-verified after every change above: 4179 cases against a
pre-SR-2 build, zero differences. Suite 805/73/194/127+2/29/7.

**The lesson, and it is not the one I would have guessed.** I had recorded "ask
which branches no test can see" as the session's best question. The critic
showed the follow-up matters as much: *when a sabotage comes back clean, do not
conclude the branch is unreachable — find the input that reaches it, then ask
why nothing in the repo supplies one.* I stopped at the first half and wrote the
weaker conclusion into a commit message.

### R5 addendum 2 — the tests critic's matrix, and the finding that mattered most

The third critic finished last and produced the most useful single artifact of
the session: 38 sabotages against a pinned `git archive c596710` snapshot, each
run through all seven suites. **20 of 38 were invisible to the entire suite.**

**The headline is F-7a, and it is uncomfortable.** Replacing
`if (r->flags & RF_CLASS_DELIM)` with `if (1)` — one token — leaves all seven
suites green. That edit FIXES K3 and its over-rejection half; it moves pcrec
strictly closer to PCRE2. So `make test` could not tell K3-fixed from
K3-unfixed, in either direction. Whoever lands the fix would have got no
confirmation, and a later refactor undoing it would have raised nothing.

That is a worse failure than a missing test. It means the project cannot
verify its own bug fixes in this area.

Closed with a **KNOWN-WRONG, pinned** block in tests/reject/: four measured
disagreements with libpcre2 asserted as they behave TODAY, labelled as bugs, with
instructions to move the lines into the real tables when K3/K4 are fixed. This
is also the answer to the ratchet problem — tests/known_fail/ structurally
cannot hold any of them, because a `.rxt` `perr` block needs the PYTHON oracle
to fail too and python accepts all four. The pin lives where the oracle is
libpcre2 and the assertions are hand-written.

**Floors with slack, and what slack buys.** tests/reject guarded `nrej >= 90`
against 93. Delete three checks, then change `\R`'s row from 'misc' to
'classes': pcrec now names the WRONG MODULE — the one fact the diagnostic
exists to carry — with every suite green. registry_check guarded `total < 60`
against 67 rows; deleting GROUP('3')..GROUP('9') was invisible, and because the
lookup then falls back to the `(?i)` catch-all, the parser routed `(?3)` to
'modifiers' and the table agreed, in unison, that this was correct. Both are now
EXACT counts. The exactness caught my own wrong guess on the first run.

**A caveat I had inherited and repeated was wrong in both directions.**
tests/registry/CLAUDE.md said the `(*` doorway is weaker than its neighbours.
Measured: the `(*` sweep DOES vary the first name byte and catches a branch on
it, while BOTH `(*` and `(?` are blind past the first byte — `(?P=` versus
`(?P<` was invisible. The honest scope is "one byte of lookahead is all any
sweep in this repo has", and registry.c's `\N{U+hhhh}` note is not one instance
of that but the general shape.

**A fair charge I have to accept.** Nine internal-error branches in ext.c are
unreachable and untested — in the same commit where D24 deferred the handler
field precisely because it "would be dead code no test can reach". The
asymmetry is real. I kept the guards (they defend against a malformed row) but
tested the INVARIANT that keeps them unreachable, and deleted the one that was
redundant rather than defensive: `if (c2 < 0)` was already handled by the
`if (!r)` on the next line.

**On the critic itself, because the method is the transferable part.** It pinned
its baseline to a commit when asked, DISCARDED the twelve sabotages it had
already run unpinned, re-ran all 38 from the snapshot, then compared the
discarded twelve against the pinned ones and reported "overlap 12, identical 12,
differing 0" — while noting that the agreement was a post-hoc check and not a
method. It also labelled the three runs it deliberately made against the live
tree and kept them out of the matrix. That is how provenance should be handled.

Suite now 805/73/199/127+2/29/7. Byte-identity re-verified after every change:
4183 cases against a pre-SR-2 build, zero differences.

### R6 addendum — the exact counts I added disarm themselves, and what T-12 reframes

The testability critic finished last and found the hole in the fix I had just
landed. R5 converted two coverage floors to exact counts. **An exact count
disarms itself for anyone who follows the failure message's own instructions.**
Measured: delete the registry rows for `\0 \3 \4 \5 \6 \7` — chosen because the
hand-written digit loop was `for d in 1 2 8 9`, so those six were covered ONLY
by dump iteration — then bump `total != 67` to `61` as registry_check invites,
then run `compliance_section.py --write` as ITS message invites. Every suite
green. `\3` then reported "unknown escape \3", i.e. pcrec claiming it is not a
PCRE construct at all.

Closed by extending the digit loop to all ten by hand, and by making
compliance_section.py's last floor (`len(rows) < 60`, seven rows of slack, mine)
exact. Re-ran the critic's exact sabotage: **7 reject failures, and `registry`
still misses it entirely** — the two-layer argument confirmed a third time, from
a direction I had not tested.

**T-12 is the finding that reframes the whole design question.** The strongest
argument for name-keyed rows is not expressiveness, it is that a MISSING row
becomes externally falsifiable: probe candidate names from outside pcrec against
libpcre2 and assert pcrec agrees. Delete a verb row, misspell it, shadow it, or
invent one — all detected, and none of those is detectable by anything in this
repo today at any effort.

But the dependency is not the selector shape. It is Q1 — a distinct
"recognised but not a known name" outcome. Without it the catch-all answers for
every name and every assertion collapses, which is precisely the over-promise
R6 measured at both the `(?` and `(*` doorways. **Q1 + PC-3 are the load-bearing
pair, both buildable against today's 67-row table.** The selector change is
secondary. That is worth knowing before anyone reaches for the interesting
refactor first.

## 2026-08-10 — session close: SR-2/3/4, R5, R6, and an order for next time

Ten commits, `cc125b6..HEAD`, all pushed. Working tree clean apart from the
uncommitted (and now gitignored) docs/wake.md. Nothing in `STATE:started`.

**Landed:** the whole SR arc — SR-2 (parse.c is the base grammar and nothing
else), SR-3 (`--list-syntax` / `--explain`), SR-4 (the dump made load-bearing) —
plus R5, the first adversarial panel over all three, and R6, a design review of
a proposal that came out of R5.

**Baseline at close, green from a fresh clone as well as in place:** 805 corpus
/ 73 CLI / 211 reject / 127 registry + 2 SR-4 doc checks / 29 codegen / 7
trie-identity, verify_rxt 796/796, fuzz seed 1 zero divergences, bench zero
budget failures.

**Six critics across two panels, and they found more than the work did.** Four
confirmed bugs (K3–K6, two of them miscompiles), one design proposal rejected
with measurements, and — the part worth carrying — **four false claims of mine,
three of which I had propagated into multiple files:**

1. "The base tier performs zero registry lookups." In six places, in D24 and
   three source files. FALSE: `[abc]` costs one, `(?:` costs zero rather than
   the documented "one, once". SR-5 was scheduled to encode it.
2. The `noreturn` attributes "fail the build". They warn. No -Werror, and no -W
   option controls that warning.
3. My byte-identity harness claimed "every byte 0x01..0xff" while `$(...)`
   silently made byte 0x0A the empty string.
4. K2's own note generalised from single digits: `(a)\12` IS octal, so
   "(backreference/octal)" is right for `\ddd` and wrong only for a bare digit.

Every one took a single measurement to check and none of them had been measured.

**The two questions that actually found things**, neither of which was on any
checklist:

- *Which of the branches I just added can no test see?* Asked because a sabotage
  returned zero. K3 was behind the answer.
- *When a sabotage comes back clean, do not conclude the branch is unreachable —
  find the input that reaches it, then ask why nothing in the repo supplies one.*
  I stopped at the first half and wrote the weaker conclusion into a commit
  message; a critic corrected it.

**An identity proof cannot see a bug both sides share.** SR-2's 4173-case proof
was correct and reported "no change" for K4 because K4 was carried across
faithfully. "Did I change anything" and "was it right to begin with" need
different instruments.

**My tooling failed four times with one signature: a check that reports success
when it has not run.** Multi-line `grep -F`; an empty replacement making a guard
vacuously true; the newline strip; and exact counts that disarm themselves for
anyone who follows the failure message's own instructions. MECH-1/MECH-2 have
been in the plan for three sessions for exactly this.

**The design conversation, and where it ended.** Frank proposed keying the
registry on whole words rather than single bytes (`(*VERB`, `[:name:]`), noted
that `^` can just be part of a POSIX name, and suggested longest-match to
separate `\N` from `\N{`. I wrote it up as SR-9; three critics rejected the
mechanism and kept the diagnosis. Adopted instead: `byte + tail`, prototyped and
measured — one field, five rows, zero parse.c changes. The reprioritisation
matters more than the design: name-keyed rows would make a MISSING row
externally falsifiable, which is the first mechanism here that scales coverage
without scaling human transcription — but that depends on **Q1**, not on the
selector shape. So Q1 and PC-3 are load-bearing and the selector change is last.

Frank also asked the forward question about `\p{...}`: nested registry tables,
canonicalised entities, handlers calling other tables. The measurements support
it — `(*` is genuinely two tables, `(?C` is a delimiter class — and the answer
for now is to build the SHAPE (a handler's currency is a SET; a row can name a
denotation) and let module `classes` prove it, since it needs `\d`/`\w`/`\s` AND
`[:...:]` and therefore needs two levels on day one.

**Next session: work docs/plan.md's four steps in order** — FIX-1 (K5/K6), PC-3
(with Q1), FIX-2 (K3/K4), SR-9 (byte+tail). See docs/wake.md.

## 2026-08-10 — FIX-1 (K5, K6) and R7, which found a third one

First of the four steps in plan.md's AGREED ORDER. Two commits: the fix, then
the panel's triage.

**Baseline verified before touching anything**, all five green in place and from
a fresh clone: 805 corpus / 73 CLI / 211 reject / 127 registry / 29 codegen /
7 trie-identity, verify_rxt 796/796, fuzz seed 1 zero divergences, bench zero
budget failures.

**FIX-1.** K5 (`a{65536}`) and K6 (`{1}`) both silently reinterpreted a
quantifier as literal text and compiled a matcher for a different language than
the pattern named — the one class the charter forbids. `try_quant` now REMEMBERS
an overflow and raises PCRE2's error 105 only where it would have returned true;
`p_atom` gained a `case '{'` that asks try_quant and raises 109 only on a yes.

Both fixes are two-phase for the same reason, and that is the part worth
keeping: the forms that must stay literal (`a{`, `{}`, `{,}`, `a{65536x}`) are
*exactly* the forms try_quant declines, so the over-reach guard is structural
rather than a second list that can drift out of step. Three orderings were
measured rather than assumed — too-big beats out-of-order, atom-position
too-big beats not-repeatable, and the offset is where the digits ran out — and a
plausible implementation gets each one wrong.

**Then the panel found K8, and it is the finding of the session.** PCRE2 (Perl
5.34) tolerates SPACE and TAB inside a quantifier. pcrec compiled `a{ 1}` as
five literal characters. Same class as K5/K6, same function, one space away from
every one of the 49 forms I had just certified the fix against — and my probes
could not see it, because they compared VERDICTS and in quantifier position both
engines exit 0. Only the compiled language differs. The critic found it by
GENERATING the brace space combinatorially instead of listing it.

Fixed the same day: a four-line `skip_quant_space` at exactly four gaps, with
the rule measured gap by gap (space and tab only; never inside a number; never
in place of one). U6 records that python agrees with the bug, which is the third
instance of that shape after `\v` and the collating elements.

**What the rest of the panel closed.** Nothing in the repo asserted an error
OFFSET, while `try_quant` kept a per-number end position for no other purpose —
so a one-token edit that made every K6 diagnostic point at the wrong brace left
all nine checks green. The over-reach guard was tested on one half of a
two-sided rule. No `{k,k}` existed anywhere in the suite, so `>` -> `>=` was
invisible. `tests/reject/` had no `timeout`, making its own "rc >= 124 is a
failure" promise unreachable — and a critic watched an un-timeout-ed call reach
6.5 GB. All fixed, each with a sabotage that was 0 before and is not now.

**The exact-count hazard finally has an answer.** R6 recorded that exact counts
disarm themselves; R7 measured it on the single row I had called irreplaceable —
move the ceiling by one, delete the row, bump the count exactly as the failure
message instructs, green `make test` in a two-line diff, on a compiler that
rejects every legal count at the boundary. `tests/reject/` now ends with a
MANIFEST that names irreplaceable rows by pattern; deleting one fails with a
message that offers no number to edit. Its first version was itself vacuous
(`[:alpha:]` matched inside `[[:alpha:]]`), which is the same lesson one level
down and is written up in the file rather than quietly fixed.

**Four claims of mine were false again, and the shape has not changed.** python's
repeat ceiling is 4294967294, not the round 4294967296 I inferred from an error
message and copied into four files. "Verdicts AND offsets agree with libpcre2
throughout" was false for one row of twenty (`{3,1}`), which I fixed in the code
rather than carry as a documented wart — all three brace diagnostics now match
PCRE2's offsets. The `# pcre2-only`/`perr` invariant I corrected in two files was
still standing, present-tense, in a third. And a compliance row dismissed
whitespace-in-braces as "reached only via constructs that are themselves
rejected" — wrong for exactly the case that became K8.

**My own sabotage harness lied to me**, which is now a four-session theme. The
`isspace()` sabotage returned 0/0 and I nearly wrote "the guard holds": the
patch had applied its `#include` and silently not its substitution, and my
vacuity check — "did the file change?" — passed on the include alone. Asserting
an exact occurrence count per replacement turned the same sabotage into a real
result immediately, and the first thing it found was that the corpus guard I had
just written for K8 was itself vacuous: a `.rxt` pattern line cannot carry a raw
control byte, and `\n` in a pattern is an escape decoded long after try_quant
has looked at the brace.

**Also found, recorded not fixed.** K7 — a large bounded repeat is SIGKILLed
rather than diagnosed, pre-existing (verified on a pinned build of c38934c). The
sharp version, measured by a critic: the `>32000 states` cap is UNREACHABLE for
`a{0,N}` because the process dies of memory first, the real threshold is
~20k–25k, and `a{0,20000}` already costs 4.7 GB to succeed. Not a miscompile;
deferred to M4 or a pre-construction size estimate.

**Suite at close:** 876 corpus / 73 CLI / 261 reject / 127 registry / 29 codegen
/ 7 trie-identity, verify_rxt 844/844, ratchet clean, fresh clone green.
**No open miscompile remains.** Next: PC-3 with Q1.

**One process note for next time.** Two of the four critics had to be prodded to
append incrementally — they had done real work and were holding it. The
instruction is in the brief and it is still not enough; ask for a first append
early rather than waiting.

### R7 follow-up — the critics' final reports, and two things they were right about

The panel's closing reports landed after the R7 commit. Most items were already
triaged and fixed; three were not, and one was a challenge to a fix rather than
a new finding.

**T-10, and it is the one I had under-rated.** `reject()` makes three assertions;
`accept()` made ONE — exit 0. So "compiles" meant only "did not say no" across
all 45 controls, and for `(?:){65535}`, which has no corpus row, that was the
entire claim. `accept()` now also requires a non-empty output file, with an `rm`
first so a stale file from the previous control cannot satisfy it vacuously.
Validated with a pcrec patched to write the file and emit no bytes, exit code
untouched: **45 controls fail, where none did before.** I had recorded this as
NOTED in the review; it deserved FIX-NOW.

**C2's swap challenge, which was the right question to ask.** It pointed out
that my three offset sabotages each left one variable unused, so
`run_trie_identity.sh`'s `-Wunused-but-set-variable` lint — the only place in
the suite treating a library warning as a failure — might still be doing the
work rather than the new assertions. Its T1b SWAPS `end_m`/`end_n` so both stay
live. Run here: 4 reject failures, zero build warnings, trie-identity 7/7 clean.
The catch is behavioural. Worth keeping: `a{65536,1}` catches the swap in the
opposite direction (7 vs 9), which is the reason to have a row whose two numbers
disagree rather than only rows where they coincide.

**A stale count in a file nobody had opened.** `tests/registry/CLAUDE.md` said
tests/reject has "93 expectations" — now 144. The passage also cites "passes
116/116 here", which is a RESULT of a dated measurement and stays, now labelled
as the count at the time. C4 flagged it as ambiguous rather than asserting it
was stale, which was the correct call and is why it got read properly instead of
being bulk-edited.

**And one honest correction to my own review.** C4 could not reconcile "49 forms
differentially probed" with the ~36 unique patterns in committed rows. Both are
true — the 49 were ad-hoc terminal probes and only some were promoted — but the
review now says so, because a number a reader cannot reproduce is a number that
will be assumed wrong later.

Suite unchanged and green: 876 / 73 / 261 / 127 / 29 / 7, verify_rxt 844/844.

## 2026-08-10 — session close: FIX-1 done, R7, and the order's first step off the board

Three commits, `c38934c..34d7e66`, all pushed. Working tree clean apart from the
uncommitted (and gitignored) docs/wake.md. Nothing in `STATE:started`.

**Landed:** FIX-1, the first of the four steps in plan.md's AGREED ORDER — K5
and K6, the two base-tier miscompiles — plus R7, the checkpoint panel over it,
plus the panel's follow-up.

**Baseline at close, green in place and from a fresh clone:** 876 corpus / 73
CLI / 261 reject / 127 registry + 2 SR-4 doc checks / 29 codegen / 7
trie-identity, verify_rxt 844/844, fuzz seed 1 zero divergences, bench zero
budget failures. Corpus 805 -> 876, reject 211 -> 261.

**No open MISCOMPILE remains.** K5, K6 and K8 are fixed; K2 (cosmetic), K3, K4
(FIX-2's target) and K7 (new, a resource bug) are open.

**The session in one sentence: the checkpoint review found more than the fix
did, again, and the reason it could is the thing worth carrying.** K5 and K6
were measured against 49 differential probes and both fixes are correct. K8 —
the same miscompile class, the same function, one space away — walked through
every one of those 49, because they compared VERDICTS and in quantifier position
both engines accept. Only the compiled language differs. A critic found it in
minutes by GENERATING the brace space instead of listing it.

**Four false claims of mine, and the shape has not changed since R5 or R6.**
python's repeat ceiling (4294967294, not the round number I inferred from an
error message and copied into four files); "offsets agree throughout" (false for
one row of twenty); an invariant I corrected in two files and left standing in a
third; and a compliance row that dismissed whitespace-in-braces as unreachable —
wrong for precisely the case that became K8. Every one was a single measurement
away.

**Three findings reduce to one question I did not ask.** T-0, T-1 and T-2 all
say: the code keeps state whose only purpose is an offset, and nothing reads an
offset. *What does this code compute that nothing observes?* is cheaper than any
sabotage, answerable from the diff alone, and would have found all three. It
belongs beside R5's "which of my new branches is invisible?".

**The exact-count hazard finally has a mechanism, not just a warning.** R6
recorded that exact counts disarm themselves; R7 measured the disarm on the one
row I had called irreplaceable, in a two-line diff, following the failure
message's own instructions. tests/reject/ now ends with a MANIFEST naming rows
by pattern. Its first version was itself vacuous through substring matching,
which is the same lesson one level down.

**And my own sabotage harness lied to me — fourth session running.** The
`isspace()` sabotage returned 0/0 and nearly earned a "the guard holds": its
patch had applied an `#include` and silently not its substitution, and my
vacuity check ("did the file change?") passed on the include alone. Asserting an
exact occurrence count per replacement turned it into a real result at once —
and the first thing it found was that the corpus guard I had just written for K8
was ITSELF vacuous, because a .rxt pattern line cannot carry a raw control byte.
**MECH-1/MECH-2 have now been in the plan for four sessions for exactly this.**

**Two deliberate behaviour changes beyond the ticket, both flagged rather than
smuggled:** the out-of-order error offset now matches PCRE2 (it was the only one
of three that did not, and carrying it meant carrying a comment that apologised
for it), and `accept()` in tests/reject/ now asserts that output was actually
emitted rather than only that pcrec exited 0.

**Next session: PC-3, with Q1.** See docs/wake.md.

## 2026-08-10 — PC-3 + Q1: the first external check, and the panel that took it apart

Second of the four steps in plan.md's AGREED ORDER. Baseline verified green
before touching anything (876 / 73 / 261 / 127 / 29 / 7, verify_rxt 844/844).

**What landed.** Q1 — the `(*` doorway now reads the NAME. Two `VerbName` tables
in registry.c, 31 upper + 19 lower, chosen by the CASE of the first byte exactly
as libpcre2 chooses between its own two, with per-name form bits recording which
spellings libpcre2 accepts. Four possible answers where there was one. And PC-3
— `tests/registry/pcre2_check.c`, the first check in this project that is not
pcrec reading pcrec: every registry row against libpcre2, plus a differential
over ~75,000 verb names in 13 forms, ~824k probes in 2.3s, with the candidate
names generated from **libpcre2's own shared object** rather than from pcrec's
table. Decision D25. Review R8.

**PC-3 found something before any critic ran.** The verb row's probe was
`(*...)`, which libpcre2 rejects — an RS_MODULE row claiming PCRE2 has a
construct it does not have. Nothing that reads only pcrec's own files could have
seen it, which is the entire argument for the step in one row.

**The panel found more than the step did, for the fourth checkpoint running, and
this time the findings were about the INSTRUMENT.** Three of the new file's four
headline claims did not survive measurement, and all three failed the same way —
a control sharing a source with the thing it controls:

- the "external" candidate pool could contribute ZERO names with nothing
  failing. 84% of the probes still ran, from mutations seeded by pcrec's own
  table; all four liveness assertions passed; the "every verb name was reached"
  guard passed; and **deleting a real verb row became invisible.** Fixed with
  provenance — every name is tagged with the source that produced it, and every
  name pcrec claims must come from libpcre2's binary independently. The critic's
  own sabotage now yields 51 failures.
- the fabrication check was defeated by one line: hide the row's syntax inside a
  PCRE2 comment. Fixed by requiring the syntax to be LOAD-BEARING — substitute
  it for `\Y` and the wrapper must stop compiling.
- `check_rows` never ran pcrec at all, so a row that had started miscompiling
  passed. Fixed; validated with a real `\K` miscompile.
- and `required_answer()` had quietly made the test file the authority on a
  question libpcre2 was never asked, certifying `(*atomic:a)` and `(*UTF)` as
  module 'verbs'. Worse, it ratcheted the wrong way: the day SR-6 routes them
  correctly the conformance test FAILS. Now: identity where libpcre2 supplies
  one, SHAPE where it supplies only a verdict.

**Two real pcrec bugs, both on axes the sweep held fixed.** `VF_EQNUM` had no
MAGNITUDE rule — the differential wrote exactly two `=` bodies, `=1` and `=x` —
and `(*LIMIT_MATCH=4294967290)` is libpcre2 error 160. The boundary is
4294967290 rather than 4294967296 because PCRE2 refuses while accumulating, one
digit early, and it is magnitude not length: `=00000000000000000001` compiles.
And a verb NAME over 128 bytes is a different complaint entirely (error 148),
which the candidate pool's 64-byte cap sat below — the cap's justification, "no
real name is longer than 30 bytes", was true and bounded the wrong thing.

**And a fix without a probe is not a fix.** Reverting the magnitude rule scored
ZERO failures in the sabotage battery: the code was right and nothing generated
an input that could see it. Two forms added; it scores 4 now. Adding the guard
is not the last step of a fix, it is the step that tells you whether you made
one.

**The silent narrowing I caught mid-work, which is the same shape one level
down.** The generic 255-byte doorway sweep asks "did the parser say *requires
module*". Before Q1 every byte after `(*` said exactly that, so it exercised
255. Q1 made most of them say "not recognized" — correctly — and the sweep
dropped to **ONE byte asserted** while still printing `PASS: all 255 bytes
agree`. Replaced by `sweep_verb()`.

**The finding I did not fix, and it is the headline.** T-12 promised the wall
comes down for the TWO name-keyed doorways. One was built. Measured: 217 of 255
bytes after `(?` are told a pcrec module will implement a construct libpcre2
rejects outright, and pcrec answers "requires module 'classes'" for all 12531
candidate POSIX class names where libpcre2 recognises 14. That is *character for
character* the `(*NOTAVERB)` over-promise D25 was built to end, at doorways 217x
and 900x wider than the one that got fixed. The escape doorway is clean — 39
rows, zero over-promises — which proves the asymmetry is not inherent but
specific to the two catch-all rows. Recorded as a second job for FIX-2 (which
already owns that doorway) and a new step Q2.

**Two claims in the plan were too big and are now corrected there.** 65 of the
67 rows are externally verified by ONE BIT; seven of RegRow's twelve columns are
read by no external check at all; and `\v` — the row this registry exists for —
is NOT verified, because libpcre2 compiles `\v` under either semantics. A critic
rewrote its note to the pre-PC-1 wrong semantics and PC-3 stayed green. That
needs a MATCH differential, which is new plan step PC-4 and cannot be built
before module `classes` lands, because every registry row is rejected today and
pcrec has no semantics to differ.

**Suite at close:** 876 corpus / 83 CLI / 180+66 reject / 127 registry + 2 SR-4
doc checks + 75 PC-3 / 29 codegen / 7 trie-identity, verify_rxt 844/844, ratchet
clean. 20 sabotages, each reverted after measuring, each caught.

**One process note.** Two of four critics again wrote a header and went quiet;
both produced their best material within minutes of a prod. The prod is now
worth budgeting for rather than treating as an exception — it has happened at
every panel since R3.

**Next: FIX-2** (K3 and K4, plus C4-7's POSIX name table), then Q2, then SR-9.

### R8 follow-up — a live wrong-module bug the panel found after the commit

C4's closing report landed after `95d18d2` and carried three findings I had not
read. One is a real bug and it is the `\v` shape, again, third time:

**`(?*...)` is PCRE2's NON-ATOMIC POSITIVE LOOKAHEAD**, the `(?` spelling of
`(*napla:...)`, and the registry had no row for it — so the `(?` catch-all
answered "requires module 'modifiers'", which is the wrong module, which is the
one fact that diagnostic exists to carry. Proven behaviourally rather than by
reading a name, on "abab": `(?*(a|ab))\1$` matches [2,4), `(?=(a|ab))\1$` does
not, `(*napla:(a|ab))\1$` matches [2,4).

**Three homes, one disagreeing.** Q1's own verb table already knew `napla`, and
docs/pcre2_compliance.md has called `(?*...)` non-atomic lookaround since the
2026-08-09 survey. Only registry.c did not. Nothing in the repo covered it —
`grep -rn '(?\*' tests/` was empty.

I swept the whole doorway rather than fixing the instance: of the 21 byte-values
libpcre2 accepts after `(?`, `*` is the ONLY one pcrec routed to the wrong
module. `(?<*...)` needs no row — it enters through `<`, which already names
lookaround.

**The other two are limits, recorded rather than fixed.** PC-3's own spec text
promised it would be "the natural home for the finding that pcrec accepts
`[:alpha:]` — findable mechanically" and that differential was not built; it
would go red today on a pinned deferred bug, so it is now FIX-2's acceptance
criterion instead of PC-3's prose. And a critic added a REAL PCRE2 construct
with the WRONG module, hit all three exact-count tripwires, followed each one's
printed remedy verbatim, and got a green `make test` with a passing PC-3. That
is the residual SR-4 deferred to PC-3 and PC-3 does not close it: libpcre2 can
say a construct exists and cannot say what pcrec should call its module. I hit
all three tripwires myself adding the `(?*` row, which is the honest
illustration — the legitimate path and the attack are the same path.

Registry is 68 rows. Suite: 876 / 83 / 181+67 reject / 128 registry / 76 PC-3 /
29 codegen / 7 trie-identity.

## 2026-08-10 — D26: functional compatibility, not bit-exact; plus limits.h and `make strict`

Frank's steer, and it is a course correction worth recording in his own terms:
*"my focus on pcre2 was to use it as the source of regex syntax and semantics
but I see a lot of effort making sure error messages are compliant... we should
be fully aligned at the core and expend less effort the further from the core we
get, particularly with regard to features we have not yet implemented, and
especially wrt features we never will."*

He is right, and the clearest evidence is mine from this session.
`(*LIMIT_MATCH=N)` has been marked OUT-OF-SCOPE in docs/pcre2_compliance.md
since the 2026-08-09 survey — it bounds a backtracking search, pcrec is O(n) by
construction, and D22 removes the adversarial-input motivation. I reproduced
PCRE2's 32-bit accumulator overflow for it to the exact digit (boundary
4294967290, not 4294967296) and pinned it in the suite. **Tier-4 work done to a
tier-1 standard, on a row we had already decided not to build** — and I did not
check our own compliance survey before spending it, which is the part worth
remembering.

**D26 records four tiers**: what a pattern MATCHES (exact), whether a construct
is REAL and which module owns it (exact), the WORDING of a diagnostic for
something unimplemented (functional — "requires module 'X'" discharges it), and
constructs the architecture rules out (clean rejection and a name, nothing
more). Two arguments make it right rather than merely cheaper: PCRE2 is a moving
target with no specification — everything R8 measured came from 10.46 and 10.47
is already out — and PCRE2 itself ships a document listing where it diverges
from Perl, so the most compatible regex library in wide use does not reach 100%
with its own namesake.

**Nothing was removed.** Frank was explicit: *"don't rip anything out — let's
just set our focus going forward."* So D26 also says what to do when an upgrade
makes a check red: tier 1/2 disagreements are findings, tier 3/4 disagreements
are DRIFT — record and demote the assertion, do not chase the new wording. That
defers the change to the moment it is needed and costs nothing now.

**It immediately paid for itself on FIX-2.** The proposed fifth doorway kind
`RK_CLASSOPEN` existed for exactly one reason: PCRE2 uses different WORDING at a
class's own bracket than inside one, so one row could not carry both. Under tier
3 one message serves, so FIX-2 now gives the `:` row `RF_CLASS_DELIM` like its
two neighbours — one flag, zero schema change — which leaves `at_class_open`
used by nothing and deletes it anyway. That was the entire benefit the expensive
option was justified by.

**src/core/limits.h.** Every number that decides what pcrec accepts, rejects or
promises, in three sections that ARE the tiers. The provenance is the point: a
bare `250` in parse.c and a bare `60` in compile.c look alike and are not — one
is PCRE2's boundary and the other is a choice we may change on a Tuesday. Both
PCRE2-derived numbers were MEASURED rather than copied from their old comments:
`a{65535}` compiles and `a{65536}` is error 105; 250 nested groups compile and
251 is error 119. parse.c called the second "a PCRE2-like nesting cap", which
undersold it — it is PCRE2's exact number. Structural constants and local
bounds with proofs beside them stay where they are; the file states its own
inclusion rule so it does not become a junk drawer.

**`make strict` (R5-Q1, answered).** Opt-in, never default — a stranger's `make`
must not fail on a newer gcc's new opinion, which is D26's argument one level
down. The project's only warnings-as-errors gate was previously ACCIDENTAL
(`run_trie_identity.sh` compiles the tree and fails on any warning) and R7
measured that accident catching a class of offset bug.

**And I broke a running test suite while adding it.** The first `strict` did
`make clean` first, which deleted `build/pcrec` out from under an in-flight
`make test` and produced a screenful of exit-126 HARNESS FAILURE lines that
looked exactly like a real regression. Rewritten to compile to `/dev/null` and
touch `build/` not at all. Validated the way any gate should be: one unused
variable in `src/core/sb.c` leaves plain `make` green and makes `make strict`
fail.

**Next: FIX-2**, built under D26 rather than retrofitted to it.

## 2026-08-10 — FIX-2: K3 and K4 fixed, and the escape rule that took three tries

Third step of the AGREED ORDER. **Landed and green, but NOT reviewed by a D6
panel** — the session was reset before it ran. That is the one process step
missing; the next session should run it before or alongside its own checkpoint.

**What landed.** `RF_CLASS_DELIM` on the `:` row, which was K3 in both
directions at once — pcrec ACCEPTED `[:alpha:]`, compiling a matcher for the set
`{: a l p h}` (measured behaviourally: the emitted binary matched ':' and 'a'
and rejected 'z'), and REJECTED `[a[:b]`, `[[:alpha]`, `[[:]`, which PCRE2
compiles. K4's three scan rules together. A measured 16-name POSIX table. The 4a
doorway sweep registry_check.c never had. And two new generated differentials in
pcre2_check.c.

**The schema question Frank was asked to steer got smaller before he answered
it.** `RK_CLASSOPEN` existed to reproduce PCRE2's two different WORDINGS at one
doorway; D26 made wording tier 3 and that reason evaporated. But a tier-2
distinction survived: inside a class the construct is one PCRE2 SUPPORTS (name
the module), at a class's own bracket it is one PCRE2 never accepts (name none).
One field, `open_msg`. No fifth kind, no RK_COUNT change, no sweep change.

**The generator changed the shape of the step before any code was written.** The
plan had five hand-pinned known-wrong cases; a generated sweep of 555
class-bracket patterns found **126 divergences**, including families nobody had
written down — `[::]` over-accepted, the whole `[[.a\]b]x.]` escape family
over-rejected. After the fix: 1341 patterns, 1325 agreeing outright, 16 honest
deferrals, **zero real divergences**.

**K4's rule 3 took THREE attempts and the instrument refuted the first two
within minutes each.** K4 wrote "skip `\]` and `\\` as a unit", which is exact. I
implemented "skip any `\X`" — refuted by `[[:\:]]`. Then "suppress only a
class-ending `]`" — refuted by `[[.a\\]x.]`. Four measured patterns separate the
three candidate rules and no weaker rule gets all four; all four are pinned, two
in the MANIFEST as the only rows ruling out each wrong rule. **I paraphrased a
precisely-worded finding twice and both paraphrases were wrong.**

**Two constructs I would have shipped as broken.** My POSIX name table started at
14 — the names I had eyeballed in libpcre2's string table. The name differential
found `[[:<:]]` and `[[:>:]]`: zero-width WORD BOUNDARY assertions, not classes
(`[[:<:]]def` matches [4,7) on "abc def"). It also found that `^` does not negate
them. **I listed a name space instead of generating it, in the very change that
added a generator** — R8's lesson, one level down, three hours later.

**And rule 2 was nearly shipped as an invisible branch.** Deleting it leaves the
1680-pattern differential at ZERO failures, because that differential compares
VERDICTS and rule 2 changes only the error OFFSET: with it, `[[.a[.b.].]` blames
offset 4 (the inner opener PCRE2 recognises); without it, offset 1 (the outer
bracket PCRE2 abandoned). D26 is what talked me out of comparing offsets, so
D26 now carries the correction: **pin your own offsets against your own
convention; do not pin them against PCRE2's.** Frank asked whether the recurring
issue is test coverage — it is not, and the distinction is in D26 now: every one
of these branches EXECUTES. The assertions project onto a SUBSET OF THE OUTPUT
FIELDS, and twice out of three the blind field was the offset.

**Suite at close:** 876 corpus / 83 CLI / 201 reject + 67 iterated (328 checks) /
129 registry / 81 PC-3 / 29 codegen / 7 trie-identity, `make strict` clean,
green from a fresh clone. K3 and K4 are FIXED; tests/reject/ carries ZERO
known-wrong pins for the first time since they were introduced.

**Next: the FIX-2 panel, then Q2 with SR-9.** PC-4 stays deferred to module
`classes`. See docs/wake.md.

## 2026-08-10 — R9: the FIX-2 panel, one session late

The one process step FIX-2 shipped without. `29a0517` was committed green and
fully documented and the session was reset before its critics ran; they ran here
instead, against the committed tree. Four critics, four lenses, own clones,
findings appended as confirmed. Two on a smaller model (record/harness, name
table), two on the larger one (instrument, rule). Review:
`docs/reviews/2026-08-10-r9-fix2.md`.

**The fix was right and the instrument was not.** Both critics who attacked the
RULE confirmed it — 1,239,480 generated patterns with zero verdict divergences,
and the 16-name POSIX table independently regenerated against libpcre2 over ~2.4
billion probes and found exactly right, no more and no fewer. Both critics who
attacked the CHECKS found defects. Three of the four findings are in the
instrument FIX-2 added; the fourth is in the docs describing it.

**C1-F1, the headline: the nested-opener shape generated no nested openers, via
undefined behaviour.** `CLS_SHAPES[9]` takes four `%c` and no `%s`; the call
site passed the body string second, so a `const char *` was read as an `int`. In
practice the low byte of a literal's address; at `-O0`, sometimes NUL, which
truncated 21 probes to the stub `[[=a[`. Which patterns the "1680-pattern
differential" probed depended on `.rodata` layout while the header kept printing
1680. `-Wall -Wextra` cannot see a non-literal format, so `make strict` was
clean. Measured cost: 42 same-delimiter nested openers in the whole sweep, all
at `:`, **zero for `.` and `=`** — the two rows where rule 2 is the offset-only
branch the commit message calls out. Replaced with a positional expander; the
sweep now generates 98/56/56 and still finds zero divergences, so this was an
instrument defect and not a compiler one.

**And the guard I added for it was wrong the same way.** The per-delimiter
liveness floor's first detector counted ONE occurrence of `[`+delimiter, which
makes `[x[=a=]]` — an ordinary inner bracket — look like a nested opener. It
read 511/504/504 and stayed GREEN when the nested shape was sabotaged away. A
control measuring something adjacent to what it names, written inside the fix
for a finding about exactly that. Only the positive control caught it. The
corrected detector requires two occurrences and reproduces C1's measurement
under sabotage: 42/0/0, two failures.

**C2-F1:** "the close check comes first because rule 1 must not consume that `]`"
is untestable — the predicates are disjoint whenever the delimiter is not `]`,
and it never is. Moving the block gave byte-identical results across all
1,239,480 patterns, against a battery where every other sabotage produced
thousands. Comment corrected; the property that makes it true is now a
`registry_check.c` assertion, because it is a fact about the TABLE.

**C3-F1:** `close_at - from` underflows for a row with RF_CLASS_NAMED and no
RF_CLASS_DELIM. Built under ASan/UBSan with such a row: no report — because
`posix_known` compares lengths before bytes, so a length near `SIZE_MAX` never
reaches `memcmp`. Safe by an implementation detail of a different function that
nothing ties to this one, and the natural optimisation of that function makes it
an OOB read. Fixed twice: `close_at` starts at `from`, and the pairing is now
required in `registry_check.c`.

**C4-F1/F2/F3:** an empty expected-substring makes `case "$out" in *""*` match
anything, silently downgrading "rejected for the right reason" to "rejected at
all" (~120 new call sites use that mechanism); the MANIFEST's "only row" for
K4's rule 3 was written twice, so a critic deleted the real one, bumped the
count 201 → 200 exactly as the file forbids, and went green; and three of four
counts in tests/reject/CLAUDE.md contradicted this commit's own headline claim,
including "5 known-wrong pins" when the point was that there are zero.

**The duplicate detector found two more the critic's inventory missed.** C4
reported `[a[.b\].]` as the only duplicate after a full-file inventory; adding a
check that reads the harness's own runtime log of what it asserted found `[:]`
and `[:a]` too. Counts corrected to 200/57 — legitimate because the removed rows
were duplicates rather than coverage, and because a recurrence now fails.
Consolidating them also surfaced a comment still calling `[::]`/`[:a:]`
"wrongly accepted (K3)", eleven lines above where FIX-2 pins them as rejections.

**One thing I got wrong at the top of the session:** the first baseline reported
`exit 0` from `make test 2>&1 | tail -30`, which is `tail`'s exit code. Re-run
properly it was genuinely green — but the project's recurring defect is an
assertion projecting onto a subset of the output, and the first command of the
panel convened to find it did exactly that.

**Suite at this point** (interim — the panel had not finished, see the second
wave below): 876 corpus / 83 CLI / 325 reject checks / 129 registry / 82 PC-3 /
29 codegen / 7 trie-identity, `make strict` clean, verify_rxt 844/844, fuzz seed
1 zero divergences, bench zero budget failures.

### R9, second wave — the panel kept working after its first findings landed

Five more findings after the first three were already fixed, one of them a LIVE
BUG in shipped code rather than in an instrument. Third consecutive panel whose
best material arrived after the point a less patient checkpoint would have
closed.

**C3-F4, the real bug.** libpcre2 accepts `[[:<:]]` and `[[:>:]]` ONLY as a
class's ENTIRE content: `[x[:<:]]`, `[[:<:]a]`, `[^[:<:]]` (a bare `^` is
enough), `[a-z[:<:]]` are all error 130, while any ordinary name works in every
position. pcrec answered "requires module 'classes'" for all of them — the exact
over-promise FIX-2 set out to remove, surviving for the two names FIX-2 itself
discovered. Fixed with `posix_whole_class_only()` plus an `at_content_start`
parameter through the doorway.

**Why both differentials missed it is the finding within the finding.** The name
sweep varies NAME across ~12000 candidates and builds every one as `[[:NAME:]]`
— position fixed. The shape sweep varies POSITION and never uses `<` or `>` as a
body — name fixed. Two large honest sweeps, and the defect in the cell of the
cross-product neither generates. Making either one BIGGER would never have found
it. New `check_posix_positions` crosses the axes; reverting the rule fails 8.

**C1-F4, the one I would least like to have shipped.** The fourteen graduated
`accept` rows assert exit 0 and a non-empty output file — "did not say no" — and
none of those patterns appeared anywhere in the .rxt corpus. A critic changed one
line so `[a[:b]` SWALLOWS the `:`, dropping it from the member set, and every
suite in the repo passed with the fuzzer at zero divergences. All verdicts right,
the set wrong. FIX-2's stated achievement is removing a class of silent wrong
matcher and its instrument never asked what was emitted. Fixed:
`tests/base/class_brackets.rxt`, 136 oracle-verified cases; the sabotage fails 4.

**C1-F2**: `check_posix_names` had no provenance requirement and its liveness was
satisfied by six non-class byte probes (`[[:]:]]` compiles because the `]` ends
the class first). Filtering PCRE2's names out of the pool AND deleting `graph`
from pcrec's table left it printing "6 real names" and three PASS lines. Its
correctness was parasitic on `check_verb_names`' assertion about a different name
space. R8/C1-F4 one doorway across. Fixed; sabotage now 10 failures.

**C1-F3**: `CLS_DELIMS = ":.="` — hand-listed from pcrec's own rows, in the file
whose header says "GENERATE the space". A critic added `if (c2 == '!')
ctx_fail(...)`, a genuine tier-2 over-rejection, and every suite stayed green.
Fixed with a 255-byte x 5-shape sweep against libpcre2. Its liveness asks a
question only the PARSER can answer — how many bytes behave differently from an
ordinary class member — rather than reading the table, which would be circular.
Answer: `:` `.` `=` and `\`, the last being the class escape.

**C1-F6**: a liveness assertion that existed only in the comment ("both buckets
must be non-empty" — one was checked). **C1-F7**: tests/registry/ had neither of
the two protections tests/reject/ has carried since R7; deleting both new
differentials and the 4a sweep left everything green, 129 -> 128 and 81 -> 76 in
output nothing compared. Both fixed.

**And C4, given a second pass, broke two of my own remedies.** The duplicate
detector false-positives on a row containing a newline (`reject()` had no display
label; `accept()` has had one since it was written), and `[ -z "$want" ]` is
defeated by a single space because every diagnostic here is an English sentence.
Both fixed; the second now rejects all-blank and records the limit it cannot
close — no floor separates a lazy `:` from a legitimately short expectation.

**What held under attack, with numbers, so it is not re-covered:** K4's three
scan rules over 1,239,480 generated patterns, zero verdict divergences; the
16-name table over ~2.4 billion independently generated probes, exactly right;
all 32 `^`-negation combinations; the position-before-name ordering; K3's
emitted matchers agreeing with libpcre2 byte-for-byte over 255 subjects; and the
200/57 count change independently confirmed honest. Also refuted: my own
hypothesis that glob metacharacters could be injected into the reject harness —
a quoted `"$want"` in a `case` pattern is literal.

**Suite at close, after both waves:** 1012 corpus (+136, the new member-set
file) / 83 CLI / 200 reject + 67 iterated (325 checks) / 129 registry / 89 PC-3
/ 29 codegen / 7 trie-identity. `make strict` clean, verify_rxt 980/980, fuzz
seed 1 zero content and zero accept/reject divergences, bench zero budget
failures. Bench ran with a critic still working (load 2.7), which can only make
it slower, so a pass stands.

**Next: Q2 with SR-9** (Frank's call — they touch the same rows). PC-4 stays
deferred to module `classes`. No open miscompile and no open over-acceptance.

### R9, third wave — two sabotages that survived the second wave's fixes

**C2-F3.** Turning K4's rule 2 off at doorway 4a for `.` and `=` only produces
1,416 over-rejections against libpcre2 and the whole repo stays green — and it
stayed green AFTER the nested-opener floor was added, because every nested
opener the sweep generated was a 4b one. Five-byte reduction: `[.[.]`, which
libpcre2 compiles as a class of `.` and `[`. Two more shapes at the class's own
bracket; sabotage now fails 12. The C1-F1 lesson recurring inside its own
remedy: the floor asked "every delimiter" when the honest question was "every
delimiter AND every position".

**C1-F8.** `check_class_brackets` counted `pc2 != 0 && rejected` as agreement
without reading pcrec's message — 746 patterns, the entire libpcre2-refuses
half, which is precisely where "is a module promised?" lives. Doorway 4a had no
external check of its own over-promise. Fixed by reading the message there, with
a mechanical way to tell a real over-promise from an honest one: append a `]`
and re-ask libpcre2, because `[[:alpha:]` is an honest deferral on a real
construct in a pattern that merely never closed, while `[:alpha:]]` still does
not compile. Baseline 0 wrong / 4 unterminated; reverting `open_msg` fails 3.

**C4V-F3, mine.** The C4-F3 fix wrote 201/67/59 into two CLAUDE.md files, and
removing three duplicates in the same review made them 200/67/57 — so the
paragraph I wrote warning about hand-copied counts carried wrong ones. Fourth
instance, second one inside the warning. MECH-1 is no longer a nice-to-have.

**C4V-F4, and a regression I caused fixing C2-F3.** The blank-only guard was
still defeated by any literal inside the diagnostic envelope: a critic collected
all 200 real diagnostics and measured `:`, `pcrec`, `pattern offset`, `(`, `)`
and the letters a e s n r t o at 200/200 each. Every message has the shape
`pcrec: <message> (pattern offset N)`, and no LENGTH floor separates `:` from
`(pattern offset 4)` — 31 rows legitimately pin an offset with that suffix. Fixed
by rejecting a want that is a substring of the envelope itself; 8/8 measured
literals refused, zero false positives on 200 rows.

And adding the 4a shapes for C2-F3 silently disarmed the nested-opener floor for
the 4b shape — 154/112/112 and green on the very sabotage the floor was written
for. The guard that caught C1-F1 stopped being able to catch C1-F1, as a side
effect of a later fix. Found by RE-RUNNING the earlier positive control after
the later change instead of assuming it still held. Six buckets now, delimiter x
position, each shape's removal firing independently. Third time this review that
a guard was wrong in the way the finding it answered was wrong.

### R9, fourth wave — the fixes attacked in turn

Each critic was sent back at the remedies for its own findings. Two results.

**C3 confirmed the C3-F4 rule generalises** — 68 patterns across nested classes,
ranges, escapes, quantifiers, groups, alternation, truncated forms and
`[^]`/`[]` shapes: 66/68 agree with libpcre2, the two exceptions being the
`[[:alpha:][:<:]]` case left deliberately. ASan+UBSan with
`-fno-sanitize-recover=all` over 18 truncated patterns plus the differential:
zero reports; `[[:<:]` hits `close_at + 2 == patlen` exactly and the bound
refuses the read.

**And it broke the liveness assertion I shipped with that fix.**
`restricted != 2` in check_posix_positions is computed entirely from libpcre2's
verdict and never reads pcrec's answer, so it stays PASS under a FULL REVERT of
the position rule — proved in a run failing 8 other checks. A real check of the
probe pool's non-degeneracy, not of pcrec, with a comment implying otherwise.
Fixed by adding the counter the name promises: how many names does PCREC vary
its own answer for by position, which must equal libpcre2's count. The full
revert now fails that 0-against-2 directly.

**C4 measured why the blank guard was still weak** — see C4V-F4 above — and
confirmed the 200/57 count change honest by diffing RUNTIME `seen` logs between
a clean 29a0517 build and the remedy build: exactly three lines removed, each
2 occurrences to 1, nothing else.

**Four times now a guard written this session was wrong in the way the finding
it answered was wrong**: the nested-opener detector counting an inner bracket;
the per-delimiter floor disarmed by adding 4a shapes; the counts restaled inside
the paragraph warning about stale counts; and a liveness assertion that measured
libpcre2 while its name claimed pcrec. Every one was caught by running a
positive control rather than by reading the code — including the two that were
caught only because an EARLIER control was re-run after a LATER change.

### R9, fifth wave — the pushed tree re-measured, and C2-F6

C2 re-ran its 1,239,480-pattern differential against `d80b452` as pushed, since
six fixes change doorway behaviour and its space had only run against `29a0517`.
**Every field identical to the digit**, including both liveness counters, and
all six sabotages reproduced their original counts — no fix weakened the
instrument's target. It then generated the axis the fix created: 161,951
patterns of `<`/`>` in every position plus a 2,400-pattern boundary sweep at
`at_content_start`, at 0 divergence and 0 true over-promise; reverting the rule
takes true over-promises 0 -> 1,841.

Its classifier was wrong first, in the signature way: it lifted the blamed
construct out and wrapped it alone (`[x[:<:]]` -> `[[:<:]]`), which compiles
because that is the ONE legal position — the control destroyed the property it
tested and would have certified C3-F4 absent. Replaced with in-place
substitution.

**C2-F6, fixed.** `CLS_BODIES` had exactly one delimiter-bearing body, the
colon-hardcoded `x[:y`, so no generated pattern ever placed a LOOSE delimiter in
a class for `.` or `=`. Dropping the `]` from the close check gave 19,964
over-rejections (`[::a]`, `[.a.b]`) with this differential's totals unchanged
and the new nested-opener floor passing; one hand-written accept row was the
whole defence. Bodies now expand through `cls_expand` as the shapes do — 2772
patterns, nested-opener counts symmetric at 112/161 per delimiter instead of
colon-skewed, sabotage fails 12.

Also corrected two comments claiming load-bearing behaviour that is measurably
dead: rule 2's `return` is identical to `break`, and the loop bound `i < patlen`
is identical to `i + 1 < patlen`. Same defect as C2-F1, twice more, in the same
function.

### R9, sixth wave — C1F-4: the guards protected existence, not size

Sent the instrument critic back at the whole remedy set asking which guard
written today another fix written today had weakened. It found the structural
form: **every new liveness floor is two-dimensional in what it probes and
one-dimensional in what it asserts.** Each sweep is `axis x SHAPES` and every
floor measures the axis; the shape axis has no floor at all.

It deleted 89% of the doorway's probes — 3371 to 359, trimming CLS_TRAILERS 7->1,
CLS_BODIES 8->2, DELIM_SHAPES 5->1, POS_SHAPES 5->2 — with every PASS line
intact, the C1-7 count guard satisfied at its exact number, and all nine
manifest needles matching. Green.

That is a direct hit on a guard added hours earlier: a count of PASS lines
protects a check's EXISTENCE and says nothing about its SIZE, and the realistic
event is not "someone deletes the differential", it is "someone trims a body
that looks redundant while refactoring". Fixed with per-sweep probe-count floors
— the mechanism tests/reject/ has used since R7. Trimming the trailers now fails
"396 probes, expected 2772", and the count guard catches it again at 94/95.

Note the recursion: the six-bucket floor was itself the fix for "the 4b shape can
be deleted invisibly", and adding a second 4a shape put that bucket back to
"*some* shape covers this". Five times now a guard written in this review was
wrong in the way the finding it answered was wrong.

### R9, seventh wave — a count cannot see a swap

Sent the instrument critic back at the three C1F fixes. It confirmed C1F-5 fires
on all three layers and that C1F-6's manifest gate opens no blind spot — it built
the case I was most worried about, one check FAILING while another is silently
DELETED, and showed the count guard sitting OUTSIDE the gate is what keeps that
caught (rc=1, and the deletion surfaces the moment the regression is fixed,
which a green run makes mandatory).

**And it found what the probe-count floors cannot do: see a SWAP.** Blanking a
shape to `""`, or replacing one shape with a duplicate of another, leaves the
probe total at 2772 and loses the same coverage with no signal. Deletions were
closed; substitutions were not. Fixed by checksumming the PATTERN SET each sweep
generates (FNV-1a, separator-terminated), pinned per sweep. Both sabotages now
fail on the checksum with the count unmoved.

Two wording defects it also caught, both the shape of the thing they sat next to:
the count guard asserted "coverage was removed" on every RED run, where a lower
PASS count is simply what a failure produces and carries no information — C1F-6's
own defect, relocated to the other half of the pair I had just fixed. And the
skip notice said "PC-3 reported failures" when the gate is also true for a
TRUNCATED run that reported none. Both now say which case they are in.

PC-3 is 98 checks.

## 2026-08-10 — SPEC-FIRST TESTING, and the tier-1 miscompile it found in an hour

Frank's diagnosis, mid-session: *"perhaps some of the issues with testing are
because the coder is writing the tests based on the code, not the goal. lets
have (at least some of) the tests written by a test writer based on reading of
the goal spec."*

Run as an experiment. Two test writers, both FORBIDDEN to read `src/` or
`tests/`. They could read CLAUDE.md, APPROACH.md, D26, pcre2_compliance.md, the
public header, and libpcre2 itself — the goal and the source of truth — and run
`build/pcrec` as a black box.

**It found a tier-1 miscompile within the hour, and it is one nothing else in
this project could see.**

`[0-[:digit:]]` — a class-opening construct as a range's UPPER BOUND. libpcre2
refuses with error 150; pcrec read the `[` as an ordinary literal member and
EMITTED A MATCHER. 546 instances in a 1,530-pattern sweep. That is the one class
the mandate forbids outright, and it had been there the whole time.

**Why every existing test missed it is the whole argument.** `a` is 0x61, `[` is
0x5b, so `[a-[:digit:]]` is rejected as an out-of-order range before the endpoint
can matter — and EVERY range in this repository is `a`-based. The bug requires a
lower bound below `[`. A test derived from the implementation inherits the
implementation author's alphabet; a writer reading only the spec picked `0-`
because nothing in the spec privileges `a`.

Scale of what it beat: four adversarial critics WITH source access, 1,239,480
generated patterns, ~2.4 billion name probes, ASan/UBSan, and the differential
fuzzer — all green, all past it. One writer denied the source found it.

Fixed by testing the construct's own recognition rule at the endpoint rather than
"is the byte `[`", with the boundary pinned against libpcre2 first: pcrec now
agrees on all 13 measured cases, rejecting the six PCRE2 rejects and still
compiling `[0-[a]`, `[0-[]`, `[0-[:]`, `[0-[:digit]` where no pair closes. Six
reject rows and four accept-controls, two in the MANIFEST — the accept side is
there because without it the fix could over-reject every `[` endpoint unnoticed.
`pcrec_ext_class_pair_opens()` shares K4's scan rather than copying it.

**The same report independently re-derived Q2** (218 of 256 bytes after `(?`
promised a module for syntax PCRE2 does not have) from the documents alone. Q2
is the next step in the AGREED ORDER and now has a second, independent
justification arrived at without reading the registry.

Still to work through from the two reports: a NUL-in-pattern API gap
(`pcrec_compile` takes no length, so `a\0b` compiles as `a`), a resource case
where `a{65535}` needs 2.1 GB / 23.9 s and aborts the caller's process under a
2 GB limit, several more tier-2 module misattributions, and SEVEN places where
the project's own documents are ambiguous or disagree — the first time anyone has
read the spec cold.

Suite: 1012 corpus / 83 CLI / 206 reject + 67 iterated (335 checks) / 129
registry / 98 PC-3 / 29 codegen / 7 trie-identity. All five gates green, and
bench GATED this time (load 5.72; the earlier runs were inconclusive at load 31
because these very spec writers were saturating the box).

### SPEC-classes-F1 — ten escapes promised a module for a non-construct

The second spec-first writer's finding, same method and the same class of
defect: `[\A]` `[\B]` `[\G]` `[\K]` `[\Z]` `[\z]` `[\C]` `[\R]` `[\X]` are
libpcre2 error 107 and `[\N]` is error 71 — PCRE2 forbids these INSIDE a class
permanently, no option and no version. pcrec answered "\A in a class requires
module 'assertions'". Module `assertions` will implement `\A`; it will never
implement `\A`-in-a-class, because that is not a construct. Tier 2 under D26,
and the same defect as `(*NOTAVERB)` and `[[:foo:]]` at the third doorway.

**The knowledge was already in this repository and inert.** The `\N` row's own
note says "any character except newline (PCRE2 forbids it inside a class)" — in
the `note` field, which R8 recorded as read by NO external check. The fact was
written down, correct, and unusable, because every test was derived from what
the code does rather than from what the row says.

Fixed with `RF_CLASS_INVALID` on those ten rows, distinct from RF_CLASS_BASE
(where the doorway is never entered — `[\b]` is backspace). Both directions
pinned: `[\b]` still compiles, `[\d]` and `[\v]` still name their module.

Both existing tripwires caught the change immediately — the in-class message
check and the 255-byte in-class sweep — which is the suite working. The sweep
now excuses RF_CLASS_INVALID the way it already excused RF_CLASS_BASE, and
check_table_to_parser asserts the refusal POSITIVELY, so being on the excused
list is not a way to escape being checked.

Suite: 1012 corpus / 83 CLI / 215 reject + 67 iterated (345 checks) / 129
registry / 98 PC-3 / 29 codegen / 7 trie-identity. All five gates green, bench
gated on a quiet box (load 0.87).

## 2026-08-10 — session close: R9, and the change to how tests get written

**What this session was for:** FIX-2's D6 panel, which `29a0517` shipped without
because a session reset. It is discharged. Seven commits, `29a0517` → `174672b`,
all pushed.

**The panel's verdict, and the shape of the whole session:** the RULE FIX-2
implemented was right everywhere it was attacked — 1,239,480 generated patterns
and ~2.4 billion name probes, zero divergences. Its INSTRUMENT was not. Thirteen
findings across four waves, then two more from a different method entirely.

**Two real product bugs, both found after the panel's own findings were fixed:**

  - `[[:<:]]`/`[[:>:]]` are position-restricted and pcrec promised a module
    everywhere PCRE2 refuses. Neither differential could see it: one varies NAME
    with position fixed, the other varies POSITION with the name fixed, and the
    defect was in the cell of the cross-product neither generates.
  - `[0-[:digit:]]` COMPILED A MATCHER for a pattern libpcre2 rejects — tier 1,
    the one class the mandate forbids.

**FIVE guards written during this review were wrong in the way the finding they
answered was wrong.** A nested-opener detector that counted an ordinary inner
bracket; a floor disarmed by the NEXT fix in the same session; corrected counts
restaled by that session's own edit, inside the paragraph warning about stale
counts; a liveness assertion measuring libpcre2 while its name claimed pcrec;
and a probe-count guard that saw deletions but not substitutions. Every one was
caught by a positive control, none by reading code, and two only by RE-RUNNING
an earlier control after a later change. That last habit is the transferable
one.

**And four of my own claims needed correcting mid-session**, recorded here
because the pattern matters more than any one of them: a baseline "green" that
was `tail`'s exit code; a glob-injection hypothesis a critic refuted with
measurements; a figure a later fix invalidated; and a "missing corpus suite"
that was two gate runs sharing one log file.

**THE DURABLE OUTCOME IS D27.** Frank's diagnosis mid-session — the coder writes
the tests from the code, not the goal — run as an experiment with two writers
barred from `src/` and `tests/`. It found the tier-1 miscompile in the first
hour, a tier-2 over-promise at a third doorway, re-derived Q2 independently from
the documents alone, and produced the first cold read of our own spec (seven
ambiguities, now DOC-1).

It beat four adversarial critics WITH source access, 1.24M patterns, ASan/UBSan
and the fuzzer. The mechanism generalises and is the part to remember: **tests
derived from the implementation inherit the implementation author's alphabet.**
Every range in this repository was `a`-based; `a` is 0x61, `[` is 0x5b, so the
masking case was rejected as an out-of-order range before the bug could show.
Isolation, not adversarialness, was the active ingredient.

Sharpest instance: the second finding's fact was ALREADY in the repo, in the
`\N` row's own `note` field — correct, and inert, because `note` is read by no
check. Knowledge the code does not act on is invisible to tests derived from the
code.

**State at close.** 1012 corpus / 83 CLI / 215 reject + 67 iterated (345 checks)
/ 129 registry / 98 PC-3 / 29 codegen / 7 trie-identity. `make strict` clean,
verify_rxt 980/980, fuzz seed 1 zero divergences, bench GATED on a quiet box
(load 0.87) with zero inconclusive. Green in place and from a fresh clone.
Nothing in `STATE:started`.

**Next:** Q2 WITH SR-9 (Frank's call — same rows), now carrying four measured
tier-2 misattributions and an independent re-derivation. Then DOC-1, and PC-4
when module `classes` lands. K7 gained a worse failure mode than it recorded
(pcrec ABORTS the caller's process under a memory limit); K9 is new — the public
API takes no pattern length, so `a\0b` compiles as `a` and reports success.

## 2026-08-10 — Q2 + SR-9: the `(?` doorway stops promising a module for 217 bytes

**The step, and why the two figures in the plan disagreed.** Q2's premise was a
document number — "217 of 255 bytes" in one place, "218 of 256" in another — so
the first thing built was not the fix but the measurement: all 256 bytes after
`(?`, 45 generated completions each, against libpcre2 10.46. **38 bytes begin a
construct; 217 of the 255 probeable ones do not**, and pcrec promised module
'modifiers' for every one of the 217. Both document figures were right from
different denominators; the 218th is NUL, which is K9's territory rather than
Q2's. Neither number needed arbitrating once the sweep existed.

SR-9 landed with it, as Frank sequenced: `RegRow` gains a `tail`, lookup becomes
longest-tail-wins inside the selector byte's bucket, and parse.c is untouched —
the §7 design predicted "0 call sites changed" and that held, because ext.c can
compute the tail context from the `Ctx` it already has.

**Six over-promises fixed. Four were on the plan; the sweep found the other
two.**

  - `(?q)` and 216 other bytes — a module promised for PCRE2 error 111
  - `(?+N)` `(?-N)` — relative subroutine calls, called 'modifiers'
  - `(?[...])` — an extended character class, called 'modifiers'
  - `(?P=` `(?P>` — a backreference and a subroutine call, both 'named-groups'
  - **`(?PX)` and 251 other tails** — bare `(?P` promised 'named-groups' where
    PCRE2 has its own error 141. Q2's defect one level down, at a sub-doorway.
  - **`(?iZ)` `(?-Z)` `(?aPP)`** — splitting the catch-all into eleven
    option-letter rows fixed the BYTE and left the RUN. A row keyed on the first
    byte cannot see the rest, so the doorway now reads the whole option run,
    exactly as Q1 made `(*` read the whole verb name.

The last one is the "fixing the narrowest instance and calling it the class"
trap the wake brief names, and it was caught only because the differential was
being written before the fix was called done.

**The run grammar was wrong twice, in opposite directions, before the
differential accepted it.** First too strict — "at most one hyphen, never after
`^`" — which UNDER-promised for 24 shapes PCRE2 calls option settings (error
194): a malformed option setting is still an option setting and module
'modifiers' is what would diagnose it. Then wrong about ORDERING, because PCRE2
stops at the first error, so `(?--D)` is 194 at the second hyphen and never
examines the `D` that would have been 111. Three candidate rules, each refuted
by measurement. K4's shape exactly, and the third time this project has paid for
inducing a rule from examples.

**The distinction that turned out to be load-bearing everywhere:** PCRE2's "no
construct here" errors are 111 and 141, and every other error means it
DISPATCHED and is complaining about the body. `(?+x)` is 129, `(?0J)` is 114,
`(?i-m-s)` is 194 — all constructs pcrec owes a module for. The option-run sweep
was first written against "does libpcre2 COMPILE it" and reported 967
mismatches that were entirely the check's own error. That verdict shape is now
recorded as D28's `SYN_OK` / `SYN_MALFORMED` / `SYN_NOT`.

**A guard that was unguarded, found by sabotage and not by reading.** Reducing
`pcrec_registry_find` from longest-tail-wins to first-tail-wins produced **zero
failures across the whole repository**. Every tail is one byte except `\N`'s
pair, and those two were written longest-first, so row ORDER stood in for the
rule. Fixed by writing them SHORTEST first — order now disagrees with the rule —
plus `check_tail_precedence`, which asserts it for every prefix-related pair and
fails loudly if no such pair remains. R9's lesson met again: when a dangerous
operation is safe because of a fact living elsewhere, the assertion belongs
where the fact is.

**And the instrument lied before the guards did.** Two sabotages first recorded
"0 failures" because the battery counted `grep -c "^FAIL"` — and PC-3's stdout
buffer flushes mid-line under load, splicing a FAIL onto the end of a PASS line
(`PASS: ...it reaches theFAIL: (? byte differential...`). `bad()`'s
`fflush(stdout)` cannot prevent it; the partial flush has already happened. A
no-sabotage CONTROL run is what separated "the guard is missing" from "my
counting is wrong", and it is the habit worth keeping — one of the two was a
real hole and the other was not, and the counts alone could not tell them apart.

**Coverage added.** PC-3 gains a 7650-probe byte differential (both populations
pinned at 38/217, so "all 255 agree" cannot be printed by a doorway that
promises a module for everything), a 19448-probe option-run sweep, and 10200
probes of tail sweeps over `(?P` `(?<` `(?+` `(?-` — each with liveness counters
and a pattern-set checksum. Six manifest entries name what each closes.
tests/reject/ gains 20 hand-written rows, because module NAMES are the one thing
no external oracle can judge: libpcre2 says a construct exists, never that pcrec
should call it 'recursion'.

Honest limits of the new sweeps, stated because they read as more than they are:
`(?<` and `(?+` answer alike for every tail under libpcre2, so agreement there is
free — only `(?P` and `(?-` have both buckets populated, which is why a
live-prefix counter is asserted and why `(?<`'s three-way module split is pinned
by hand instead.

**D28, and a step inserted.** Frank's call mid-session, from a real question:
option-run parsing had nowhere good to live. `ext.c` exists so parse.c holds the
core syntax and nothing else — its job is routing a matched extension to a
handler, not accumulating every construct's body parser — and `registry.c` is
declarative data. The enumeration settles it: ten construct families need body
parsing, and the two largest (`\p{...}`, which needs NORMALISATION rather than
validation, and `(?[...]`'s nested set algebra) are ahead of us. So a module
gets PORTS — semantic, syntax, and optimisation later — and the doorway
identifies the construct from key+tail before calling the syntax port for the
details. The argument that settles it over one handler with a mode flag is
LIFECYCLE: every module is unimplemented today and body parsing is still
required for all of them, because tier 2 is exact under D26.

[MOD-0] is inserted after this step: define the ports and build two or three
real modules to shape them. `pcrec_registry_option_run_ok` sits in registry.c
PROVISIONALLY, with a comment saying so, and is the first thing MOD-0 moves.

**State at close.** 1012 corpus / 85 CLI / 397 reject / 164 registry / 143 PC-3
/ 29 codegen / 7 trie-identity, all green. `make strict` clean, verify_rxt
980/980, fuzz seed 1 zero divergences. Registry is 100 rows (was 68).

**THE PANEL IS OWED.** Frank's steer was to close this commit knowing MOD-0 will
rework the interface, so no D6 critic panel was run. That is a deliberate
deferral, not an oversight, and it is recorded here rather than left to be
noticed: FIX-2's panel ran a session late as R9 and found thirteen findings plus
two live product bugs, so a deferred panel is a real debt. Run it against
MOD-0's result, and brief it on THIS change too — in particular on the option-run
grammar, which no adversarial reader has seen.

**Next:** MOD-0. Then DOC-1, then PC-4 when module `classes` lands.

---

## 2026-08-11 — MOD-0 design session: the recogniser, and a conflation caught before it was built

**No code changed.** This session was design only: D29, an amendment to D28,
MOD-0 expanded into eight substeps, and two documentation drifts fixed in
passing. Baseline verified first (§2 of the wake brief) and green.

**What Frank changed.** The shape I brought into the session was D28's — the
doorway identifies a construct from key+tail, then calls the row's syntax port
for the body. Frank's reframe: make the port a RECOGNISER of one proper form,
put several of them on one selector byte, call all of them, and expect exactly
one to answer. *"In this guise, perhaps this function supersedes the tail part
entirely."* It does, and the argument that settles it is `\N`: today `\N` and
`\N{U+...}` are resolved by LONGEST-TAIL-WINS, a rule that arrived unguarded
with row ORDER standing in for it. As recognisers they are disjoint predicates,
and a naive `\N` recogniser that matches everything makes BOTH fire — a loud
registry defect where there was a silent precedence. Ten `(?-0)`..`(?-9)` rows
also collapse to one recogniser, because they are one construct written ten
times only because a tail is a literal prefix rather than a pattern.

**THE FIND, and it is why Frank's "re-examine what we assumed" question earned
its keep.** He asked, before any write-up, whether using a function here had
ramifications we were missing — problems or missed opportunities. It did.
D28's `SYN_OK / SYN_MALFORMED / SYN_NOT` is a taxonomy of PCRE2'S ERROR
NUMBERS, measured correctly, and I had been treating it as a taxonomy of what
the DOORWAY does. They are different axes. `pcrec_ext_class_bracket` already
implements three doorway answers and `SYN_NOT` conflates two of them:

    [[:alpha:]]   CLAIM     PCRE2 recognises it            -> name the module
    [[:foo:]]     REFUSE    PCRE2 errors, permanently      -> this message, no module
    [a[.b]        DECLINE   PCRE2 COMPILES it as something -> carry on, not mine

REFUSE and DECLINE are opposites and both map to `SYN_NOT`. K3, K4, FIX-2 and
R9/SPEC-FA were each a local instance of that distinction being got wrong, so a
vocabulary unable to express it would have re-created all four. Caught in
review, before a line of it was written.

**Five more things that fell out of the same question.**

- **Recognition must not depend on the body parsing**, because PCRE2's does not:
  `(?i:(` is still an option group (dispatched, then error 114). A recogniser
  that recursed into the body would watch it fail and DECLINE — exactly the
  UNDER-promise Q2 made and the differential refused. So the recursion lives in
  the semantic port, and that is also the better argument for TWO ports than
  D28's lifecycle one: a predicate and a parser cannot share a signature.
- **Recognisers allocate nothing, and that dodges K7.** The obvious repair for
  `\p{...}`'s normalised name is to pass an `Arena *`. Measured:
  `arena_alloc` calls `abort()` on malloc failure (`src/core/arena.c:15`), which
  IS K7. Spans plus a caller-provided fixed buffer instead, so K7 does not
  spread across the module layer.
- **Frank asked whether a semantic port could just call the parser recursively,
  since it is recursive descent.** Yes — `p_alt` at `parse.c:500` — and it makes
  parse.c and the modules MUTUALLY RECURSIVE, which is a change to the stated
  architecture (D24/`src/parse/CLAUDE.md` call ext.c a router with modules as
  leaves). Adopted deliberately and written down. One depth counter, not two:
  `cx->depth` against `PCREC_MAX_GROUP_DEPTH` (`parse.c:242`,`:266`). The payoff
  confirms the shape — `(?i:...)`'s semantics are literally "set parse state,
  parse body, restore", which cannot be written without the callback, so the
  SIMPLEST module is the one proving the callback is needed.
- **Row options have exactly one customer.** Frank proposed passing the row
  options so a `tail_default` recogniser could check a literal tail as the
  lookup does today, and asked whether options had any other use — he could not
  think of one. Neither could I, after checking every family that shares an
  algorithm across rows: the discriminator is always `sel` or the module's own
  data. So no generic option field. `const char *tail` stays; only its READER
  changes, from the lookup engine to one recogniser.
- **Where DATA stops and CODE starts.** Turning flags into functions partly
  reverses what D24 bought. The line adopted: a flag stating a citable FACT
  about the construct stays data (`RF_CLASS_INVALID`, `RF_CLASS_NAMED`); a flag
  meaning "call a special scanner" becomes the recogniser pointer
  (`RF_OPTION_RUN`, `RF_CLASS_DELIM` both retire). D27's mechanism is the reason
  facts must stay visible: knowledge the code does not act on is invisible to
  tests derived from the code, which is exactly how SPEC-classes-F1 hid in the
  `\N` row's own `note`.

**Opportunities recorded, and one is the answer to a worry I had raised.** I had
argued against port output fields nobody reads, since wake §6 counts seven
RegRow columns already in that state. `--explain` is the answer: it consumes
what was recognised, the answer, the blame offset and the normalised name, from
a CLI surface testable in tests/cli (MOD-0.7). Also: a module's measured PROBES
travel with its recogniser, which extends SR-1's "a new row covers itself" from
rows to BODIES and directly answers R8/C2-9's drift; and
`pcrec_ext_class_pair_opens` collapses, being a second copy of the scan K4 got
wrong three times.

**Three modules chosen, and why those three.** `modifiers` moves regardless — it
is the debt MOD-0 exists to pay — but it is not one of the three, because D28 is
right that shaping on the simplest body inherits its alphabet. `classes` is the
richest INPUT case (context flags, an open-ended scan, and the only doorway
where DECLINE is normal). `verbs` is the MIGRATION TEST — existing measured
code, four answers, form bits, a non-default blame offset. `unicode-props` is
the only NEW recogniser, the case that breaks a validate-only signature, and
the only part a D27 spec-first writer can test blind. It should also produce a
live tier-2 finding: `\p` promises its module for every tail today, which is the
Q2 shape at a fourth doorway.

**Landmines written down before they are stepped on** (D29's own section): the
exact row count moves and R8/C4-10 measured that following the tripwires'
printed remedy is how a wrong module passes everything; `(?:` would carry a dead
recogniser nothing calls; and the class-bracket doorway is on the BASE-TIER path
(once per non-negated `[`), so the cost of running all recognisers there gets
measured or not claimed — SR-5 has not run.

**Two documentation drifts fixed in passing.** `tests/registry/CLAUDE.md` said
the exact row count was 68; it has been 100 since Q2/SR-9 — an exact-count
tripwire failing to prevent drift in its own documentation. And
`src/parse/CLAUDE.md`'s `tail` bullet now carries a forward reference to D29, so
a reader does not follow a rule MOD-0.2 is about to retire.

**Next:** MOD-0.1 — the interface, with the `\N` / `\N{U+` ambiguity pair
written FIRST as its acceptance test.

## 2026-08-11 (same session, later) — R10: the design panel, and the warning we had already written

**Still no code.** Frank asked for a hostile critic pass on D29 before anything
was built. Five critics, five lenses, ~2,400 lines of findings, all read-only.
Compiled review: `docs/reviews/2026-08-11-r10-mod0-design.md`. D29 now carries
inline `[R10]` corrections and a REFUTED-IN-PART status block; MOD-0.1 and
MOD-0.2 are `STATE:blocked`.

**The result: D29's spine survives, its central guard does not.** The
recogniser-per-row idea, the two ports with two signatures, the semantic port
recursing into `p_alt`, no-allocation-in-recognition, and
row-options-have-one-customer all stand. "Exactly one recogniser may answer",
the retirement of `check_tail_precedence`, both proposed controls, and four
measured facts do not.

**The finding that matters most, and it is D27's mechanism turned on the
designer.** `src/parse/registry.c:62-72`, written 2026-08-10 — the day before
D29 — says in as many words: *"Do not design a handler signature that assumes it
can."* `\ddd` is octal or a backreference depending on the running capture
count, which decides its MODULE, which is tier 2 and EXACT. D29 does not cite
it, does not answer it, and specifies exactly that signature. C3 measured the
behaviour rather than trusting the comment: `(a)x11 \12` is octal, `(a)x12 \12`
is a backreference, `(?n)` flips it back, `\Q..\E` and class parens do not
count, and `\1..\9` uses a whole-pattern count instead. D27 says knowledge the
code does not act on is invisible to tests derived from the code. R10 adds that
it is equally invisible to DESIGNS derived from reading the code — reading
`registry.c` for its data while designing a signature is precisely the reading
that skips a comment about signatures.

**"Exactly one may answer" fires on a CORRECT registry.** Every tailed bucket has
a tail-less FALLBACK row, and that row's honest recogniser is "always matches" —
which D29 called naive and presented tripping the guard as the guard working. In
the `\N` and `(?P` buckets the fallback and a sibling hold OPPOSITE verdicts, so
two honest recognisers answer and the table is right. Silencing it means
hand-encoding longest-tail-wins inside each function: **D29 retires the rule and
keeps the obligation.** D29 also described its own acceptance test wrongly — the
prefix-related pair is `{` vs `{U+`, not bare `\N` vs `\N{U+`, and there is no
`}` in the construct.

**And it was the wrong KIND of guard.** `check_tail_precedence`'s second half is
REACHABILITY; the replacement is UNIQUENESS; they catch disjoint classes.
Proved on D29's own proposal: `-\d+)` declines on `(a)(?-1` (error 114 —
malformed body, still the construct), so the "simplification" is a tier-2
regression. Deferred.

**Both proposed controls were the defect they were meant to cure.** `--explain`
never enters a doorway — it is a prefix match on the `syntax` column, and D29's
own worked example does not run. A swapped module attribution passes every
existing case10 assertion, demonstrated twice. And "probes travel with the
module" is co-location (the DRIFT cure) applied to a CIRCULARITY problem;
`pcre2_check.c` already carries the anti-circularity rule D29's scheme lacks.

**The measurement lesson, in its purest form yet.** "17 tailed rows, measured"
was measured — by one grep, for a macro NAME, on a table containing one tailed
row not written through a macro. It is 18. Two critics found it independently by
iterating the table. The missed row is `\N{U+`, the centrepiece of the argument
the number supported, miscounted twice in two different ways in the same
passage. **Counting a population by the syntax used to write it counts the
syntax, not the population.**

**What the panel confirmed, which is also a result:** `arena_alloc`'s abort IS
K7 — reproduced live under `ulimit` with a gdb backtrace, a stronger method than
the static read D29 used. `PCRE2_UTF` flips no construct verdict (the wake §6
claim a critic was briefed to falsify). `(?x)`/`(?xx)`/`(?J)`/`(?n)` move no
doorway recognition boundary. Two critics appeared to disagree about `(?x)` and
did not: option state changes BASE-GRAMMAR lexing, not doorway recognition,
which shrinks one finding and enlarges another.

**The generalisation worth carrying, sharper than D27 reached it:** D29's three
defences were all LIVENESS arguments — is there a reader, does the loop run, is
the space generated — where every failure this project has recorded is a VALUE or
a SET argument: can the reader dissent, can the loop be disarmed, who chose the
input. Ask of any new guard **not "does this check run" but "what would have to
be true for it to fail, and who chose that input".**

**A process result: a DESIGN panel beat every implementation panel on cost.** R9
found thirteen findings in built code; R10 found comparable severity in a
document, and every fix is an edit to a paragraph rather than to a shipped
construct. Worth repeating before the next interface, not after it.

**Next:** the redesign, per R10's eight dispositions. Frank's call on the
replacement resolution rule — it is a real design fork and the panel deliberately
did not choose it. Nothing is committed yet.

**ADDENDUM, same session — and it is a finding about the process, not the
design.** C3 had written NOTHING at the 15-minute poll while the other four
critics had 107-723 lines. Prodded per the standing lesson; produced 233 lines.
I read those 233 lines, wrote the R10 review, corrected D29, updated the plan,
and had `make test` running for the commit — and C3 then tripled to 739 lines
with four more findings, one of which corrects D29's FOUNDING SENTENCE. **The
commit was minutes away and would have gone out on two thirds of one critic's
output.** wake §1 step 3 exists for exactly this (R8's panel sent its best
finding after the commit) and R10 nearly repeated it. The rule to carry: **the
prod is necessary and NOT sufficient — poll again AFTER the prod, and do not
treat a critic's first delivery as its last.**

What that late half contained:

- **C3-7: "recognition must not depend on the body parsing" is FALSE as
  written**, and D29 contradicts it two paragraphs earlier by nominating
  `pcrec_ext_class_bracket` — a function whose entire body is a body scan — as
  the model implementation of the three answers. Measured: PCRE2's recognition
  depends on the body in five shipped constructs (`[a[.b]` vs `[[.a.]]`,
  `[[:foo:]]`, `(?iZ)`, `(*LIMIT_MATCH=`'s magnitude, `(*pla:x` vs
  `(*ACCEPT:x`), and in the base tier `a{1}` vs `a{x}`. The correct sentence is
  narrower and survives every probe: **recognition must not depend on parsing a
  NESTED PATTERN — it must never reach back into `p_alt`.** Scanning an opaque
  body is not merely permitted, it is mandatory.
- **C3-6: `p_alt` is not a usable callback as the code stands.** The group node
  is ERASED (`(a|b)|c` and `a|b|c` generate byte-identical C), so a
  `conditionals` port cannot recover the branch count PCRE2 needs for error 127;
  and the depth decrement sits after the doorway call, on a path a module never
  reaches. MOD-0 therefore includes a parse.c change, which D29 does not price.
- **C3-5: `(?[...])` nests, capped at 13**, so a "pure, no failure path"
  recogniser needs its own bounded stack and depth rejection — a second depth
  budget in the layer that just insisted on one.
- **C3-10: the bare-fallback hazard is FOUR buckets, not one**, widening C1-3
  from the other lens.
- **C3-3b, refuted harder than asked:** `(?x)` set MID-PATTERN and SCOPED still
  moves no recognition boundary. That is what makes the leftward option
  dependence narrow and nameable instead of pervasive.
- **C3-9: the one D29 opportunity the panel CONFIRMED** — collapsing
  `pcrec_ext_class_pair_opens` holds, and the shipped scans agree with libpcre2.

R10's dispositions now run to twelve.

**ADDENDUM 2 — and the same thing happened twice more, which is the real
process finding.** Having written the addendum above about C3, a final re-poll
before committing showed C1 had grown 645 -> 758 and C2 393 -> 680 **since I had
read them**. Three of five critics delivered substantial material after their
files were read and after compilation had begun, and that late material contains
the panel's ONLY live product defect and its STRONGEST design finding. The
amended rule, now in R10 and worth more than any single finding here:
**re-poll every findings file after the last prod and immediately before
compiling, and diff the counts against what you actually read. A critic's first
delivery is not its last, and "I have read this file" decays.**

**K10 — a LIVE tier-2 defect, recorded in docs/known_issues.md.**
`[\N{U+41}]` is answered "\N is not valid inside a character class"; libpcre2
gives error 193 in every class position including as a range endpoint, which is
recognition-then-mode-refusal. The `{U+` row carries `RF_CLASS_INVALID` while
its own `note` says error 193 is "recognition, not rejection" — the row
contradicts itself. R9's SPEC-classes-F1 named ten escapes and the flag landed
on an eleventh. Verified independently before recording. The fix is one flag;
the TEST is the work, so it is scheduled with MOD-0.6 rather than patched here.
**The fourth net is the one to remember:** `registry_check.c:875-876` exempts
`RF_CLASS_INVALID` rows from the in-class sweep, so the flag exempts the row
from the only check that would contradict it — a control taking its scope from
the field it controls.

**C2-8, the strongest design finding, and it indicts the method rather than the
detail.** The `(*` doorway ALREADY has four answers: D25 is titled *"a 'not a
known name' outcome DISTINCT FROM 'requires a module'"* and `(*MARK)` is pinned
in three places. PCRE2 recognises `MARK`, so under D29's CLAIM row pcrec owes
"requires module 'verbs'" — and deliberately does not. **One enum cannot carry
"CLAIM the construct but name no module", and that cell is occupied by shipped,
tested code.** Why it was missed: D29 derived its three answers from ONE doorway
(`pcrec_ext_class_bracket`), a sample of size one — then cited D27 three
sections later and applied it to the recogniser SIGNATURE while not applying it
to the VERDICT ENUM. **The same document states D27's rule and breaks it, two
pages apart.**

**And a sequencing hazard the plan created and did not notice (C2-11):**
`(?xx)[a- ]` compiles where `[a- ]` is error 108, because `xx` deletes the
space — at the class range endpoint SPEC-FA fixed one commit ago. MOD-0.3
(`modifiers`) was scheduled BEFORE MOD-0.5 (`classes`), and pcrec's only current
guard is that `(?x)` is unimplemented. MOD-0.3 now carries the gate.

R10's dispositions run to sixteen. Suite re-verified green after all doc edits
(`make test` rc=0, zero `FAIL:` counted unanchored).

## 2026-08-11 (same session, close) — D30: the seven questions R10 left open, answered

Frank went through R10's open questions one by one and took the recommendation
on all of them. **D30** records the resolution; D29 stays as committed, with its
`[R10]` marks, because the refutations are the reasons. Still no code — MOD-0
is now a designed step rather than a blocked one.

**The ranking was MEASURED before adopting, not argued.** Ranks hand-assigned as
0/25/40/70 — deliberately not `strlen(tail)`, so the mechanism could not be tail
length renamed — then compared against today's engine over a generated
depth-0..3 suffix space across every multi-row bucket:

    multi-row-bucket probes: 176544   agreements: 176544
    disagreements: 0   equal-rank collisions: 0   zero answers: 0

Sabotaged both ways: inverting `{U+` vs `{` → 1 disagreement; making the
fallback outrank its siblings → 21,437.

**Rank dissolves R10's central objection.** C1-1 said the only way to keep the
guard silent was to hand-encode longest-tail-wins inside each recogniser —
"D29 retires the rule and keeps the obligation". Under rank **no recogniser
needs to know its siblings**, the bare fallback answering "always" at rank 0 is
CORRECT rather than naive (dissolving C1-3 and C3-10 outright), and precedence
goes back to being DATA, which is the side of D24's line it belongs on.

**And the caveat is the interesting part.** Inverting the one genuinely
prefix-related pair is observable on **exactly one input in 176,544** — the same
n=1 fragility `check_tail_precedence` documents about itself. So its LIVENESS
CLAUSE is carried over rather than retired with it. That is R9's lesson landing
in a new place: a guard that can stop having anything to watch must say so.

**Which is why C4-6's per-row check becomes the PRIMARY instrument, not the
sweep.** *A row's own `syntax`, fed to its bucket, must be won by that row and
no other*: 22 rows, TOTAL, terminating, no generated space, no oracle — the
properties C4-5 noted the static `(sel,tail)` check had and a sweep loses. It
scored 1 and 18 against the same two sabotages, catching by construction what
the 176k sweep caught by a single probe.

**What none of it covers, and it is written down as open by design:** C1-2's
malformed-body reachability. `-\d+)` still declines on `(a)(?-1`. Closing it
needs an external oracle — *pcrec must promise a module wherever libpcre2
DISPATCHES* — so that differential is part of MOD-0.1 and the `-\d+)` collapse
does not land until it passes.

**Six other resolutions, in one line each.** The doorway's answer stops being an
enum and becomes (dispatched?, compiles?, whose message?), because `(*MARK)`'s
"CLAIM the construct, name NO module" is shipped and pinned and no enum carries
it. The compile MODE is bound and written down as PCREC's decision, so `\U` is
REFUSE *because pcrec will not offer ALT_BSUX* rather than by a false claim
about PCRE2 — and the quantifier's five axes (construct, position, context,
mode, version) are named. `p_alt` is fixed FIRST, as new step [PARSE-1], because
it is base-grammar work on the hot path and the callback should exist before a
module needs it. The digit buckets are a STATED exception: shape only, module
attribution deferred to the semantic port, which is the one place D29's "the row
names the module" genuinely fails. `classes` now precedes `modifiers`, closing
the scheduled `(?xx)`-at-a-range-endpoint window. K10 ships known with MOD-0.6,
Frank's call, at the cost of `tests/reject/` no longer carrying zero known-wrong
pins.

**The methodological note worth keeping from D30 §3.** D29 derived three answers
from ONE doorway while citing D27 three sections later and applying it to the
recogniser SIGNATURE but not to the VERDICT. The same document stated D27's rule
and broke it two pages apart. **Apply D27 to every enumeration, not only to
signatures.**

**Next:** [PARSE-1], then MOD-0.1. Nothing about the recogniser is built yet,
and that is now the first thing that has been fully specified rather than
sketched.

## 2026-08-11 — SESSION CLOSE

**Three commits, no behaviour change, and MOD-0 went from a sketch to a
specification that has survived a hostile panel.** `2aca7dd` -> `695f937` (R10)
-> `6fa6331` (D30), all pushed. Suite green at every commit: `make test` rc=0
with the status captured directly, zero `FAIL:` counted UNANCHORED.

**The arc.** D29 was designed with Frank across four turns, written up, then
attacked by a five-lens panel BEFORE anything was built — the first design panel
this project has run. It refuted the central guard, four measured facts, and
both proposed controls, and turned up one live product defect (K10). D30 then
resolved the seven questions R10 left open, with the replacement mechanism
MEASURED and SABOTAGED before adoption rather than argued.

**What the session produced, in order of durable value:**

1. **A working resolution mechanism, verified.** Declared rank reproduces
   today's selection over 176,544 probes with zero disagreements and zero
   collisions, using ranks that are deliberately not tail length. Both sabotages
   fire. The per-row `syntax` check is total over 22 rows with no oracle.
2. **The knowledge that a DESIGN panel is the cheapest review available here.**
   R9 found thirteen findings in built code. R10 found comparable severity in a
   document, where every fix was an edit to a paragraph.
3. **Two sharpened process rules** — below, and both are now in wake.md.
4. **K10**, a live tier-2 defect, found by a critic probing a guard rather than
   probing the product.

**Rule 1: the prod is necessary and NOT sufficient.** Three of five critics
delivered substantial material AFTER their findings files had been read and
compilation had begun — including the panel's only live defect (C1-7) and its
strongest design finding (C2-8). C3 had written nothing at the 15-minute poll,
produced 233 lines after a prod, and then tripled to 739 after those 233 were
read. **Re-poll every file immediately before compiling and diff against what
you actually read.** "I have read this file" decays.

**Rule 2: apply D27 to every ENUMERATION, not only to signatures.** D29 derived
its three-answer verdict from ONE doorway while citing D27 three sections later
and applying it correctly to the recogniser signature. The same document stated
the rule and broke it two pages apart. The `(*` doorway already shipped four
answers, adopted in D25 and pinned in three places.

**And the one that stings, worth keeping for that reason.**
`src/parse/registry.c:62-72` — *"Do not design a handler signature that assumes
it can"* — was written 2026-08-10, the day before D29 specified exactly that
signature. D27 says knowledge the code does not act on is invisible to tests
derived from the code. R10's addition: it is equally invisible to DESIGNS
derived from reading the code, because reading a file for its DATA while
designing a signature is precisely the reading that skips a comment about
signatures.

**State at close.** 1012 corpus / 85 CLI / 397 reject / 164 registry / 143 PC-3
/ 29 codegen / 7 trie-identity, all green. Registry 100 rows. `parse.c` is still
the base grammar and nothing else — PARSE-1 will be the first change to it since
FIX-1. Open defects: K2 (cosmetic), K7 (resource), K9 (API contract), **K10 (new
— tier 2, live, scheduled with MOD-0.6)**. `tests/reject/` no longer carries
zero known-wrong pins; that was a deliberate call.

**Owed and carried forward:** the Q2+SR-9 panel debt still rides on MOD-0.8, now
alongside R10's own follow-ups. DOC-1 (seven spec ambiguities) and PC-4 are
untouched; PC-4 is now further away, since `classes` moved but the semantic work
did not start.

**Next session's queue is written in docs/wake.md** with gates, journal
discipline and the review requirement per step. First step is [PARSE-1].

## 2026-08-11 (new session) — PARSE-1's design: a third defect, a corrected diagnosis, and 928 probes

**Baseline verified first, all green at `e595a0e`.** 1012 corpus / 85 CLI / 397
reject / 164 registry / 143 PC-3 / 29 codegen / 7 trie-identity, `EXIT=0`, zero
`FAIL:` counted UNANCHORED. `make strict` 0. `verify_rxt.py` 980 PASS / 0 FAIL
(100%). `fuzz.py --seed 1` zero divergences. `make bench` 0 budget failures,
load 0.74 -> 0.80 across it, measured BEFORE any critic was spawned.

**D5 amended, at Frank's instruction.** Asking permission before convening a
panel was ruled a MISREADING: subagents are used AS NEEDED on this project, no
per-occasion approval, and a lower model is the default where the work fits one.
Recorded in D5 and in the root CLAUDE.md conventions.

### Three defects in `p_alt`-as-a-callback, not the two R10 measured

(a) and (b) are R10/C3-6's. Both re-verified today rather than taken on trust:
`(a|b)|c` and `a|b|c` still generate C differing only in the pattern comment and
the `#include` name.

**(c) is NEW and was not in R10's list.** `src/core/internal.h:138` holds
`const pcrec_options *opt`; `parse.c:80` and `:224` are the only two sites that
fold case and both read `cx->opt->caseless`. So the scoped parse state D29 names
as the callback's entire payoff — *"modifiers' semantics are literally set parse
state, parse body, restore"* — does not exist: the state is `const`,
caller-owned and whole-compile, and `(?i:a)b` cannot be expressed.

**How (c) was found is the point, and it is D27 turned on the author.** R10's
two defects came from reading the code, and reading the code finds the defects
the code can express. (c) came from asking what the FIRST MODULE needs and then
checking. Same method, one level up from where D27 applies it.

### The diagnosis in R10/C3-6 and D30 §5 is partly WRONG, and this is the finding

R10: *"a `conditionals` port calling `p_alt` back cannot recover the top-level
branch count."* True only of recovering it FROM THE AST AFTER THE FACT.
**`p_alt` already computes the number and throws it away** — its
`while (peekc(cx) == '|')` loop counts branches, and `p_atom` consumes a whole
group as ONE atom, so the erasure at `:275` sits strictly BELOW that loop and
cannot perturb its count. `(?(1)(a|b)|c)` counts 2; `(?(1)a|b|c)` counts 3.

**The group node being erased is real, and it is not what blocks error 127.**
Committing to a structural `A_GROUP` on that reasoning would have been building
a node to fix a problem it was mis-diagnosed into.

### 928 probes, libpcre2 10.46, options = 0 — the class is TWO constructs

32 construct families that take a nested pattern body x 29 generated bodies
(branch counts 1..6, leading/trailing/middle/all-empty branches, sub-runs
wrapped, nesting at depth 1 and 2). Exactly two families' verdicts depend on the
body's top-level structure, and they are the same fact at different thresholds:

    conditionals, ALL 13 condition forms   err 127   > 2 branches
    (?(DEFINE)...)                         err 154   > 1 branch

Empty branches COUNT — `(a)(?(1)|)` compiles, `(a)(?(1)|b|c)` is 127 at offset
3. A group counts as ONE branch, which is why `(?(1)(a|b)|c)` compiles while
`(?(DEFINE)(a|b)|c)` still fails.

PROBED AND HELD, 29 each: branch reset `(?|...)` (unbounded — 50 branches
compile), lookahead/lookbehind pos+neg, non-atomic forms, atomic groups,
plain/non-capturing/named groups, `(*pla:` `(*plb:` `(*napla:` `(*nla:`
`(*atomic:` `(*sr:` `(*asr:`. `(*scs:` is 115 on all 29 for an unrelated reason.

### A wrong claim of my own, recorded because the wrong version is instructive

I inferred that a wrapper node would defeat D9's prefix trie and regress bench
case (d), which is literally `(alpha|beta|gamma|delta|epsilon)` — a group
wrapped straight around a 5-branch alternation with a throughput budget on it.
**Measured, and it is false.** `build/pcrec` and a scratch `-DPCREC_NO_TRIE`
build emit byte-identical C for that pattern and for `(?:alpha|...|epsilon)`.
The trie is OUTPUT-PRESERVING by construction (`nfa.c:162-165`,
`run_trie_identity.sh`), so it cannot move a throughput benchmark at all.

What it actually costs is PCREC'S OWN COMPILE TIME, and that is worth a lot:

    (?:prefix000_suffix|...|prefix299_suffix)   trie 0.017s / no-trie 0.256s  15x
    (?:w1|...|w150)|(?:w151|...|w300)           today 0.036s / bound 0.263s  7.3x

And the regression is NARROW: a wrapper around a whole alternation sits ABOVE
the spine, so a pass-through case recurses and the trie survives. Only a group
wrapping a PROPER SUB-RUN of an outer alternation de-flattens.

### What the fact-gatherers established (both delivered only after a prod)

Two sonnet subagents, both header-only at the poll, both delivering in full
immediately after being prodded — 31 -> 263 and 30 -> 387 lines. The rule holds
for fact-gatherers, not only for critics.

- `sizeof(Ast)` is 72; `arena_alloc` rounds to 16 so every node costs 80; 819
  nodes per 64 KB block. A wrapper is +1 node per group, and `(...)` and `(?:...)`
  share the path, so N is ALL parenthesised groups.
- `compile_ast`'s switch has **no `default:`** — a new `AKind` is a `-Wswitch`
  WARNING under plain `make` (build still succeeds) and only an error under the
  opt-in `make strict`.
- **NOTHING in `tests/` asserts on the AST at all**, and the
  `(a|b)|c` == `a|b|c` byte-identity is pinned by NO automated check.
- Both doorway bodies were traced exhaustively: no `return` on any path, so the
  depth counter cannot leak TODAY and the defect is entirely latent.
- **And the bigger half of (b), which neither R10 nor I had stated:** if
  `pcrec_ext_group` returned a node, control would fall through into `p_alt` at
  `:263` and **the node would be silently DISCARDED** — nothing at `:256-263`
  distinguishes "handled" from "fall through to a plain group". (b) is not a
  missing decrement; it is that the group case has no control shape in which a
  doorway can answer at all. A fix that only moves `cx->depth--` leaves the
  silent-discard intact, which is the more dangerous half.

**Design panel convened** on the candidate design (four lenses: the
recommendation, control flow, scoped state, checks). Nothing built yet — the
gate is findings triaged first.

## 2026-08-11 (same session) — PARSE-1 built: the panel moved the design twice

**Panel: four lenses on the candidate design, before a line was built.** Two
delivered in full (C1 249 lines, C4 413), one partially (C2 53), one after a
SECOND prod (C3 8 -> 71). Every substantive finding was a correction to the
author's own document, which is what a design panel is for.

**AND THE RE-POLL RULE SAVED THE SESSION.** After reading C4 at 244 lines and
C3 at 8, a final re-poll immediately before building showed C4 at 413 and C3 at
71. C3's late material contained the finding that changed the shape of the fix
(below) and C4's contained the built-and-sabotaged instrument the design was
missing. R10 added "re-poll every file after the last prod and immediately
before compiling"; this session is the second consecutive one where it was
load-bearing rather than a courtesy.

### What the panel changed

**C1-3 — the currency was wrong.** The design said "one integer". `ctx_fail(cx,
pos, ...)` takes a POSITION as a REQUIRED argument, so a module cannot RAISE
error 127 from a count alone — and the critic checked the tier rather than
assuming it: **D26 puts pinning pcrec's OWN offsets against pcrec's OWN
convention in TIER 2**; only chasing PCRE2's number is tier 3. `Ast` has no
position field, so leaving the AST alone forecloses recovering one afterwards.
Adopted its proposal: `AltInfo {nbr, last_bar}`, a struct, at the same cost.

**C3-1 — defect (c)'s fix is the SAME EDIT as defect (b)'s.** Measured 17/17
against libpcre2: `(?i)` set inside a group stays in force to the end of THAT
group, **leaks across that group's sibling alternation branches**
(`(a(?i)b|c)d` matches `Cd`), and restores at the immediately-enclosing `)`,
not the outermost. That boundary is structurally identical to the depth
boundary — so the save/restore belongs in the base grammar's group case, NOT in
`modifiers`' semantic port, and the parser must not need to know a module fired.
I had been about to defer (c) as scope creep; it is two lines of the edit I was
already making.

**C4-1 — the primary check was refuted, and the sabotage is live.** Asserting
`(a|b)|c` == `a|b|c` in emitted C is passed by a build containing NONE of
PARSE-1: the property held BEFORE the feature existed, and candidate B's whole
design is that the AST does not change. Verified on the unmodified tree for five
shapes. Kept as a FORWARD-pointing regression net; its claim demoted in three
places so no reader cites it as evidence the feature is present.

**C4-2 — I cited the wrong liveness precedent, and copying it ships a red
build.** `check_tail_precedence` calls `bad()` (exit 1) when its subject
vanishes, because the property WAS live and going dead is a regression a
maintainer caused. Depth balance and caseless scoping were NEVER live — they
need code that does not exist. Wiring them to `bad()`, which is what a builder
copying the CITED mechanism would do, leaves `make test` permanently RED from
PARSE-1 until MOD-0.2. `pcre2_check.c`'s loud-SKIP-exit-0 is the right
precedent. Both now print on every run.

**C4-4 — the missing check, built and sabotage-verified by the critic.** The
design proposed nothing that checked the COUNT IS RIGHT, and wrongly framed it
as blocked on pcrec implementing conditionals. It is not: libpcre2's thresholds
are functions of that number alone, so libpcre2 stands in for the module pcrec
does not have — PC-3's shape exactly. The critic built a reference counter and
validated it over 343 bodies with two sabotages scoring 9/2 and 9/1 mismatches.

**C1-1 — the sweep omitted this document's own next consumer.** 32 families,
and `modifiers` was not among them, despite §0 naming it priority 2 one page
above. Closed (36 probes, no dependency); two verb spellings likewise (27
probes, held). Benign outcome, real method gap: D27's alphabet lesson applies to
a set the author GENERATED as much as to one they listed.

### Built

`p_alt_info` reporting `AltInfo`; the group case split into `p_group` (entry and
exit bookkeeping, one path each) and `p_group_body` (owns neither end);
`cx->caseless` seeded once in compile.c from the const caller-owned options and
saved/restored at every group boundary; `pcrec_parse_info` as the seam a check
can reach.

**Behaviour-preserving, and asserted rather than assumed: 690 generated patterns
compared against a binary built from HEAD — identical stdout, exit code and
stderr on all 690.**

### The new suite, and its sabotages

`tests/parse/`. 16,384 generated bodies; pcrec agreed with an independently
written reference counter on every one; libpcre2 arbitrated that reference
32,768 times with ZERO disagreements. Three sabotages of the reference caught.
Then the stronger control: **three sabotages of `p_alt` ITSELF** — always report
1, stop incrementing, over-increment — each rebuilt in a scratch tree and each
caught, 12,288 failures apiece.

### Carried forward

**A doorway that returns a node still has its node SILENTLY DISCARDED.** PARSE-1
fixes the depth symptom; the control shape is MOD-0.1's, and
`pcrec_ext_class_bracket` (the only one of four not `noreturn`) is the shipped
precedent its contract should derive from.

Two module-level facts found by the fact-gatherers, recorded so MOD-0 does not
rediscover them: a conditional can SELF-SATISFY off its own body —
`(?(1)(a|b)|c)` compiles with no preceding group, because PCRE2's numeric
condition tests whole-pattern existence — so `conditionals` needs a
whole-pattern capture count, generalising D30 §6 beyond the digit buckets; and
error 127's OFFSET is form-specific (0/3/6/11/12/13). Also: the capture count is
TWO mechanisms, not one — incremental for `\ddd`, whole-pattern for `\1..\9`,
the latter a forward reference wanting a lexical pre-scan. `[MOD-STATE]` owns
it; `p_group_body` now carries the hook comment so it is not a third renovation
of the same lines.

**C3 also argues `modifiers` may not need the callback at all** — its result IS
its body, so it could be a second special case alongside `(?:` falling through
to the existing body parse. If so, D29's motivating example does not motivate,
and the callback's real forcing cases are `conditionals` and `lookaround`.
SUSPECTED, falsifiable, and worth settling before MOD-0.5.

### PARSE-1 gate: green, and one operational finding

    make test    EXIT=0 — 1012 / 85 / 397 / 164 / 143 / [parse 2+5] / 29 / 7
                 (every pre-existing count UNCHANGED; FAIL: counted unanchored, 0)
    make strict  whole tree compiles clean with -Werror
    verify_rxt   PASS=980 FAIL=0, 100%
    fuzz --seed 1  zero divergences
    make bench   hard errors 0, budget failures 0, every section PASS,
                 load 0.63 -> 0.71 with no critic running

Bench (d) — `(alpha|beta|gamma|delta|epsilon)`, the case I had WRONGLY predicted
a wrapper would regress — came in at 455.1 MB/s against a 448.7 MB/s baseline,
which is the final confirmation that the trie is output-preserving and the whole
concern was misdirected.

**`make bench` first failed, and the failure is worth recording because `df`
lies about it.** `HARNESS FAILURE: python3 subject generation failed`,
`OSError: [Errno 122] Disk quota exceeded` — with 1.6 GB reported free. `/tmp`
on this box is a tmpfs with a PER-USER QUOTA, and prior sessions' scratchpads
had 5.4 GB of it. Reproduced with `dd`: 72 MB of writes succeed and the next
64 MB does not, at 1.6 GB "free". Fix used: `TMPDIR=/var/tmp make bench`,
pointing at the 98 GB root filesystem rather than deleting another session's
data. Recorded in tests/bench/CLAUDE.md. wake §3 was right that HARNESS FAILURE
is distinct from a budget failure; it was wrong about the cause being free
space. **`hard errors: 1 / budget failures: 0` means the benchmark DID NOT RUN
— do not read the zero as a pass.**

## 2026-08-11 (same session, follow-up) — R11's late material arrived AFTER the commit

**The process failure first, because it is the finding.** `0ebbdc7` was
committed with C2's findings file at **53 lines**. It finished at **680**. This
is R8's recorded failure — *"do not close a checkpoint until the reports are in
hand"* — reproduced in a session that had already applied R10's re-poll rule
TWICE successfully. The rule as written stops at "immediately before compiling";
C2 delivered after the commit. **Extend it: the checkpoint is not closed until
every critic has idled, not until the build is green.** Recorded rather than
smoothed over, and the fixes below are a follow-up commit rather than an amend.

### What the late material actually contained — one of it was a real miss

**`p_alt` had NO LINKAGE (C2-8), and that was PARSE-1's own stated purpose.**
The step is titled "make `p_alt` a usable module callback". `p_alt` and
`p_alt_info` are `static` to parse.c, so ext.c cannot call either, and
`pcrec_parse_info` — the one thing PARSE-1 exported — is the WRONG entry point
for a nested body, because it requires end-of-pattern and ctx_fails on `)` with
"unmatched closing parenthesis". **A module handed it would fail on every body
it was given.** I had fixed the count, the depth and the parse state and left
the callback uncallable. Fixed now: `pcrec_parse_body`, which parses a body and
stops AT its terminator without consuming it, the caller consuming its own `)`.

**The contract guidance I committed was wrong (C2-5/C2-10).** `0ebbdc7` told
MOD-0.1 to derive `pcrec_ext_group`'s contract from `pcrec_ext_class_bracket`'s
"or justify differing". The justification exists and the answer is DIFFER: the
two doorways' non-fail outcomes are DISJOINT. class_bracket's three `return;`
sites never write `cx->pos` — its only normal-return outcome is DECLINE with the
cursor unchanged. The `(?` doorway can never decline at all, because
`registry.c:505`'s catch-all is REJECTED, so its only future normal-return
outcome is CLAIM with the cursor past its own `)`. Corrected in three places.

**The silent-discard defect is REPRODUCED and is an exit-0 miscompile.** One
selector byte returning a node, and `(?%x)b)` compiles byte-identically to `b` —
the module's node and the pattern's own unmatched `)` both vanish, no
diagnostic, exit 0. Still MOD-0.1's, now recorded with the repro.

**"These two checks cannot fail today" was FALSE (C2-9).** A fixture doorway on
a selector byte no registry row uses makes depth balance observable NOW, no
module needed. So the whole SKIP-vs-`check_tail_precedence` argument was the
wrong question for these two: they are UNOBSERVED, not unobservable. Text
corrected; MOD-0.1 should ship real checks rather than either precedent.

### And the depth checks I then wrote were themselves blind, which is the better lesson

Added cap probes (250 accepted / 251 rejected, both sides, `(...)` and
`(?:...)` — matching C2's 780-probe measurement). Then sabotaged them, and:

    double-decrement sabotage -> *** PASSED. The check was BLIND. ***

A purely nested pattern only tests the cap on the way IN; a leaked decrement
shows on the way OUT, where nothing was looking — and it fails OPEN, the
dangerous direction. The input that catches it is SEQUENTIAL groups first, then
a nest one past the cap. Added. Then `no-decrement` passed too — it fails
CLOSED, needing the opposite probe (600 sibling groups at real depth 1 must
still compile). Added.

**Four depth sabotages now verified caught: double-decrement, no-decrement,
no-increment, off-by-one cap.** The balance probes exist because a sabotage
found the blindness, not because anyone foresaw it — which is the whole argument
for sabotaging every check rather than running it once and believing it. My own
first probe also failed for a stupid reason (`-o /dev/null` makes pcrec write
`/dev/null.h`, permission denied, so every ok-side probe "failed" correctly for
the wrong cause) — caught only because the check went red immediately.

`tests/parse/` is now 7 checks. Full gate re-run below.

**Follow-up gate, all green:** `make test` EXIT=0, 0 `FAIL:` unanchored,
1012 / 85 / 397 / 164 / 143 / [parse 2 + 8] / 29 / 7. `make strict` clean.
`verify_rxt` 980 PASS / 0 FAIL. `fuzz --seed 1` zero divergences (the state-cap
lines are the known DFA limitation, labelled as such by the harness itself).
`TMPDIR=/var/tmp make bench` 0 hard errors, 0 budget failures, every section
PASS.

One last check added, from C2's final delivery (823 lines — it grew AGAIN, from
680, after the follow-up was written): **the base-tier group diagnostic must
have exactly ONE home in `src/`.** Total, terminating, no generated space, no
oracle. It guards the thing `pcrec_parse_body`'s contract makes tempting — a
module copying "missing closing ) for group" instead of writing its own
construct-appropriate wording, which is `\v`'s two-homes shape (D24).

**And the first cut of that check scored 3 on a CORRECT tree**, because two of
its three hits were comments in this repository explaining that the string is
single-homed. **A check that counted prose about itself.** Anchored on
`ctx_fail(` it reads code, scores 1, and catches a planted second call site.
Third time this session a check was wrong on first writing and only sabotage or
an immediate red said so.

## 2026-08-11 (same session) — MOD-0.1's design panel: D30 refuted in part, nothing built

**[MOD-0.1] is STATE:blocked, deliberately.** The panel ran against a WRITTEN
DESIGN and refuted enough of D30 that the interface needs re-resolving — the
same shape as R10 → D30, so it wants a D32 and that is Frank's call. **Every
finding cost a paragraph instead of a commit**, which is the argument for design
panels stated once more.
Full record: `docs/reviews/2026-08-11-r11-parse1-mod01.md`, seven dispositions.

### The headline: D30 §2's non-optional check is FALSE, measured

D30 §2: *"pcrec must promise a module wherever libpcre2 DISPATCHES."* Over 1,672
generated probes at all four doorways, options = 0, libpcre2 10.46:

    libpcre2 DISPATCHED (diagnostic names a construct)   769
      of which pcrec promises a module                   676
      dispatched but NO module promised                   93
    libpcre2 says NOT-A-CONSTRUCT                        206
      pcrec named a module anyway (OVER-promise)           0

**All 93 are pcrec being CORRECT** — 40 REFUSE (`\U`/`\u`, D30 §4's own bound
mode), 20 POSIX collating, 16 BASE-TIER constructs pcrec implements, 6 unknown
POSIX names, 4 `\N{name}`, and 1 `(*MARK)` which is D25's deliberate fourth
answer. **"Dispatched" does not imply a module is owed**; that needs the other
two of D30 §3's three facts. §3 gets it right and §2 ignores it two sections
apart — the same "states the rule and breaks it" failure §3 diagnoses in D29.

Clean positive: **0 over-promises in 206 not-a-construct probes.** Q1's, Q2's
and FIX-2's cleanups hold over a space none of them generated.

### Rank is almost entirely unchecked, and two of the three checks coincide

5,632 probes — all 22 bucketed rows x candidate rank in [-5,250]:

- **20 of 22 rows accept ANY value up to 250** with no proposed check failing.
- The one prefix-related pair is a single THRESHOLD, not an ordering: crossing
  40→70 is caught, the other 68 interior values pass silently.
- **The per-row `syntax` check and the rank sweep fire on IDENTICAL boundaries
  in all 5,632 cases.** D30 requires both; one adds nothing.
- Module-swap is invisible to the per-row check (R10/C4-1 one level in, on a
  TIER 2 property); row deletion is invisible to both (R5's incident again);
  `check_tail_precedence` cannot be retired because its liveness obligation has
  no committed successor.

Positive: "two answering rows at equal rank is the defect" does NOT repeat
D29's bug — 0 collisions over 3,507 probes on the correct table.

### The returning-doorway defect is FOUR call sites, and one is UNDEFINED BEHAVIOUR

D31 recorded one instance. Measured, the class is worse. `pcrec_ext_escape` is
called from `esc_atom` and `esc_class_value` as the LAST STATEMENT of a
value-returning function with **no `return`** — legal only because `noreturn`
makes falling off the end unreachable. Make it return:

    a\qb    (esc_atom → Ast*)       exit 0, compiles, the stub node reaches the
                                    matcher — pointer relaunched out of %rax by
                                    calling-convention accident. 5/5.
    [a\qb]  (esc_class_value → int) SIGSEGV, exit 139. build/pcrec — THE
                                    COMPILER ITSELF — crashes. 3/3.

Two failure shapes, two call sites, one binary, one change. Unlike the group
case (well-defined C, deterministically the same wrong answer) **this is UB.**
It is also the only doorway where the compiler warns at all — two
`-Wreturn-type`, build still exit 0; group and verb warn ZERO for the identical
change, because discarding a return value is silent in C.

Flagged, not reproduced: `esc_class_value`'s return feeds
`cls_set(a->cls, (unsigned)lo)` with NO range check, and `cls_set` indexes
`b[c >> 3]` into a 32-byte array.

And the group-discard class, generated not listed — 18 patterns: **7 are
byte-identical to a SMALLER pattern** (`(?%x))` → the EMPTY pattern;
`(?%x)(?%y)c))` → `c`, two discards compounding; `(?%x)(d))` → `d`, a real
nested group absorbed), 8 give a spurious "missing closing ) for group", 2 give
the wrong quantifier error, 1 a misattributed offset. **0 of 18 behave as the
contract promises.**

### Facts that survive and should be reused rather than re-measured

100 rows / 18 tails / exactly **4** multi-row buckets, by iterating
`pcrec_registry()` rather than grepping macro names — the method that produced
17 where the answer was 18. All 18 tailed rows live inside those buckets, which
hold **22 rows — D30's own figure, independently derived**. D30's undocumented
0/25/40/70 rank mapping was recovered and verified 22/22 two ways. **`ext.c`
never reads `.tail`**, so its six call sites need no change and only three files
touch the field. ~~`find()`'s same-length tie-break falls back to SOURCE ORDER — a
latent branch that rank converts into a loud defect, which D30 never claims.~~
**[RETRACTED the same session — see the addendum below. The second half of that
sentence is false and the first half is unreachable.]**
And **existing external coverage of tailed rows is 2 prefixes, not the 10,200
probes it looks like**: `check_group_tails` runs 4 prefixes x 255 bytes x 10
completions, but for `<` and `+` libpcre2 agrees on every tail, so they prove
nothing.

### Process, and it cost something this time

**The panel ran 2-of-4.** M3 (349 lines) and M4 (184) delivered; two produced
only headers and were re-run with narrow single-question briefs. Recorded as a
finding: **a five-part critic brief delivers materially worse than a brief with
one clear primary item.**

One fact-gatherer died before writing up — but because it wrote raw data
incrementally, its four sweep TSVs survived and the analysis was done from them.
The incremental-write rule paying off in a case it was not designed for.

### MOD-0.1 panel close — one answer, and one gap I am not glossing

**M5 (re-run on a narrow brief) settled the signature:** the recogniser's last
parameter is `const char *tail`, NOT `const RegRow *self`. Answered by
enumerating all 22 bucketed rows, not from principle — no row needs any other
field. The reason to refuse `self` is that a recogniser able to read
`self->module` becomes a second, contradictable home for a TIER 2 fact, and
**the rank guard polices ANSWERS, not which fields a function consulted**, so
nothing would catch the drift. The one genuinely hard bucket (`(?-`'s digits,
where `\12` is octal-or-backreference by capture count) is out of a pure
recogniser's reach regardless of signature, so it argues for a third kind of
input to the SEMANTIC port, not for handing recognisers the row.

**THE GAP: my reachability measurement was never independently reviewed.** The
critic assigned to attack it produced only a header — twice, on two
differently-scoped briefs. So "D30 §2 is false" currently rests on ONE
measurement, taken by the person who found it interesting. That is the exact
shape this project distrusts everywhere else, and R11 says so in its own text
rather than letting the number stand unqualified. The probe corpus and
classifier are kept so someone else can reproduce it before D32 leans on it.

**Nothing was built for MOD-0.1 and nothing should have been.** The tree is
unchanged from `5d4663f` apart from documentation.

### ADDENDUM — five agents delivered AFTER the R11 commit was pushed

**Third occurrence this session, and this one corrected a claim already in a
pushed commit message.** M1 (recorded header-only) produced seven findings; M2
(recorded as producing nothing, twice) produced the panel's sharpest refutation;
G2 (recorded as having died before writing up) produced a 253,963-probe
corroboration; M3 and M4 both appended more.

**And the rule I had just written was followed and still failed.** *"A
checkpoint is not closed until every critic has IDLED"* — `ListAgents` reported
no reachable agents before the commit, while five agents still had output to
deliver. So the honest version is weaker: an agent-list check is EVIDENCE, not
proof, and the only real protection is that a follow-up commit is cheap and
normal. Recorded in R11's addendum in that weaker form.

**RETRACTED: the `find()` tie-break claim.** I asserted in R11, plan.md, the
journal and commit `9504e8a`'s message that `find()`'s same-length tie-break
falls back to source order and that rank converts it into a loud defect.
Verified in code: the tie needs an IDENTICAL `(sel,tail)` pair, which
`registry_check.c:184-193` already forbids unconditionally — so the branch is
unreachable. And rank would NOT make it loud: a counter-example was built and
run — two duplicate-tail rows at ranks 25 and 26, both plausible hand-typed
values, produce zero collisions and the higher rank silently always wins. That
is SR-9's own failure shape relocated from "row order" to "whichever integer is
bigger". Corrected in all three files.

**The gap R11 flagged is CLOSED — the measurement was corroborated twice.** G2:
253,963 generated truncated probes, zero genuine gaps, zero over-promises, 1.6s
linking libpcrec.a directly. M2: 3,164 independent probes, 0 over-promises,
0/104 residue across the `(?-N` malformed space. **And both hit the same trap
independently** — G2's first two-way classifier produced 7,516 FALSE gaps and
M2's produced 236 FALSE over-promises. The classifier must be THREE-way and
PER-DOORWAY calibrated; a uniform code set breaks on VERB.

**M2 refuted the residue formula: 46 of its own 93 counterexamples (49%) fit
none of its three exclusions.** There is NO registry row for `\U`/`\u`/`\F`/
`\L`/`\l` — the answer comes from `ext.c:84-85`'s generic fallback — and
"unknown POSIX class name" is a function (`registry.c:913-918`), not a row. PC-3's
circularity defence is literally true and beside the point: most of the evidence
was never a row. **Most actionable line in the whole panel:** `ext.c:85`'s
generic `"unknown escape \%c"` is the project's ONLY completely unguarded
diagnostic surface — nothing would notice its wording changing.

**M4's highest-value finding: `pcrec_ext_verb` has the IDENTICAL discard defect**
— same function, two lines above the `?` branch, same fallthrough — and is named
in NONE of mod01-design.md, D31, or D31's addendum. A fix touching only the `?`
branch ships incomplete with no test able to catch it.

**M1 found two signature defects:** `head_len`'s contract breaks for
`RF_OPTION_RUN` rows (the option run starts AT the selector byte, one before
every other recogniser's `at`), and `span_at`/`span_len` have no consumer at all
— D24/SR-2's own "lost more to unexercised structure than to missing structure".
Also: option (B)'s cost premise was false, since all 22 rows use one identical
generic recogniser.

Six further dispositions (9-14) added to R11. **M6 was still running when this
was written; its result folds in when it lands, and the finding no longer
depends on it.**

### M2, fourth tranche — the baseline number, and a shipped guard on its floor

**The honest baseline for MOD-0.1's check (c), which nobody had written down:**
by the four multi-row buckets — `\N` has **0% external coverage (no sweep for
the `\` doorway exists at all)**, `(?<` is nominal but structurally vacuous,
`(?P` and `(?-` are live and already correct on garbage-before-paren. So **2 of
4 buckets have any live coverage, 0 of 4 have complete coverage of the
malformed-body class, 1 of 4 has none.** That is the number to beat, and D32
should state it.

**`check_group_tails` cannot generate an unterminated body.** Verified in
source: `TAILCOMP[]` (`pcre2_check.c:1780-1782`) has ten completions and **every
one ends in `)`**. So R10/C1-2's own forcing example `(a)(?-1` is outside the
instrument BY CONSTRUCTION — the existing differential covers "digit + garbage +
`)`" and is blind to "digit + nothing", which is exactly the shape the `-\d+)`
collapse would regress. The new check EXTENDS this one; it does not duplicate it.

**And a shipped guard is sitting on its floor.** `pcre2_check.c:1832` is
`if (live_prefixes < 2) bad(...)` — a COUNT, not a per-prefix expectation — and
exactly two prefixes are live today. **If `-` went vacuous while any other
prefix became live for an unrelated reason, the total stays 2 and the guard says
nothing** — losing coverage of the one prefix the collapse depends on, silently.
That is wake §8's silent-narrowing shape inside a guard written to prevent it.
Dispositions 15-17 added.

Circularity ruled out for that instrument: `check_group_tails` never reads
`RegRow.tail` — it generates all 255 bytes directly, so its gaps are GENERATION
gaps, not circularity leaks.

### M6 — third confirmation, and a hole in my own criterion found by luck

M6 reported last. **The reachability finding now rests on three independent
harnesses** (G2 253,963 probes, M2 3,164, M6 58,709 + 435 for the nested class
doorway): 1,392 dispatched-no-module cases, 0 anomalies, 0 counterexamples, 13
(doorway, code) buckets triaged by hand. The gap R11 flagged is closed.

**And M6 found that R11's published criterion is INCOMPLETE.** It names the
"no construct" code for GROUP (111/141) and VERB (160/195) and never names the
ESC doorway's own: **103, "unrecognized character follows \"**. Verified myself
by sweeping the alphabet — 52 letters split into 29 compiles, one distinct code
per real-but-incomplete construct (102 `\c`, 137 ALT_BSUX, 146 `\p`, 155 `\o`,
157 `\g`, 169 `\k`, 178 `\x`), and exactly **11 letters at rc=103: i j m q y I J
M O T Y**.

**The published counts are unchanged, and that is the damning part.** Re-running
my own 1,672-probe corpus with 103 added gives identical numbers — 769 / 93 /
206 / 0 — because the corpus contains ZERO rc=103 probes. My escape alphabet was
HAND-LISTED and happened to omit all 11 letters that would have exposed the
hole. **I hand-listed an input space and got away with it by luck, inside the
measurement I used to refute D30 — the exact failure wake §8 and D27 name, in a
document that cites both.** The numbers survive; the method did not.

M6 also refuted part of my own disposition 11: a rival GLOBAL BLACKLIST
criterion (ignore which doorway produced a no-construct code) gave counts
IDENTICAL to the per-doorway version, delta 0 across its whole space. So
per-doorway calibration is not measurably necessary; the three-way split and
complete per-doorway CODE COVERAGE are. Dispositions 18-19 added.

## 2026-08-11 (same session) — R12: a comparative design panel, and both designs lost something

Frank proposed an alternative to D30's recogniser+rank design after reading R11:
**an ordered list of parser functions**, one per row, each deciding AND parsing,
first match wins, called with a copy of `Ctx` and a `trial` flag so a
speculative call could be abandoned. It was written up and panelled against D30.
Full record: `docs/reviews/2026-08-11-r12-d32-comparative.md`.

**Four narrow briefs, one primary question each — 4 of 4 delivered**, against
R11's 2 of 4 with five-part briefs. That format difference is now measured twice.

### Design B's precedence rule died on the shipped table, needing no edit

Its loop run against `registry.c` as it stands gets its own canonical example
wrong twice: the tail-less `\N` fallback is declared FIRST (`:242`) so it claims
`\N{U+0041}` before anything else (16/17 probes), and even pinned last, `"{"`
(`:254`) precedes `"{U+"` (`:257`) so the short prefix wins (7/17).

**And the irony is exact.** `src/parse/CLAUDE.md:166` records those rows are
written SHORTEST first DELIBERATELY, so `check_tail_precedence` would have a real
prefix-pair to observe. **The hardening that made the old check meaningful is
exactly what breaks the new rule.**

Structural finding: order has a failure mode rank cannot have — **global
positional coupling**. Moving `RK_GROUP`'s catch-all to position 0 breaks 54 of
the other 55 rows, none touched. And B's own repair can't cover B's reason for
existing: a static position check is buildable but reasons only about `tail`
strings, while B demotes `tail` and lets functions claim beyond it — **the check
covers exactly the rows that don't need design B.**

### Trial mode died by being built

The loop calls the function once and commits only after it RETURNS, so any
construct with a body must allocate inside the trial-covered call — which under
a literal trip aborts every CORRECT implementation. So a handler must clear the
flag first; the critic wrote `cx->trial = false;` as line one and allocated
freely, and **the trip did not fire**. It is mutable state on the struct the
checked code owns a pointer to. Design A's boundary (a pure recogniser has no
`Ctx *` at all) cannot be defeated that way; B's can, by construction.

It also **buys nothing over design A for its own motivating customer** —
`pcrec_ext_class_pair_opens` is safe to call speculatively only because it is
already pure. And the arena leak I called "waste, not corruption" was wrong by
orders of magnitude: **~76-80 bytes leaked per byte scanned, 76.4 MB at
N=1,000,000**, unreachable from the real `Ctx` so `arena_free` frees none of it.

### Five of my own claims refuted

trial mode "strictly stronger than A's type guarantee" (false); the arena leak
being benign (false, by orders of magnitude); the per-row `syntax` check getting
"stronger" under B (true but irrelevant to the module-swap blindness I cited it
for); my `sel`-redundancy check (vacuous as worded — passes for all 100 stub
rows, R11/C4-1's shape again); and the three-outcome protocol, which **would have
resurrected the over-promise FIX-2 removed**, for three of the class `:` row's
four terminal shapes.

### The third shape, which neither of us proposed

Both designs arbitrate BETWEEN ROWS IN A BUCKET — and two of the four doorways
already have no such mechanism, because ONE function handles the whole bucket
(`pcrec_ext_class_bracket` for all three class rows; `pcrec_ext_verb` for D25's
four answers and both name tables). Generalising that gives **one function per
bucket**: precedence becomes `if`/`else` inside one function — local, greppable,
diff-visible, testable in isolation — which **deletes both precedence mechanisms
and every check either of them needed.**

It honours P1's finding that a decide/build boundary must be STRUCTURAL, but
proportionately: the boundary is only needed where something asks speculatively,
and there is exactly ONE such customer in the parser, already pure, at one
doorway. Three doorways need no split.

**NOT yet panelled** — it emerged from this panel and has not been attacked.
That is the next step, and it wants Frank's call first.

## 2026-08-11 (same session) — D32: the interface resolved, after three panels

**[MOD-0.1] is UNBLOCKED.** D32 is written. It took R10 (refuted D29), R11
(refuted parts of D30) and R12 (refuted the alternative and produced the
resolution) to get here, and the resolution came from Frank pushing back on a
premise nobody had examined.

### The thing that unlocked it

Every refutation since R10 rested on *"every tailed bucket has a tail-less
FALLBACK row whose honest recogniser is 'always matches'"* — R10/C1-1. Frank
asked for an example of a genuine ambiguity, and there isn't one: written as
proper forms the four buckets are disjoint. That "honest" was honest about the
TAIL, not about the CONSTRUCT — an artifact of the lookup mechanism being
replaced.

But the author's first repair (write disjoint forms, so `\N` reads "N not
followed by `{`") was WORSE, and Frank named why: it puts negative knowledge of
every sibling into every function. **His version keeps functions POSITIVE and
LOCAL — `\N{U+` asks only "does it start with `{U+`" — and lets RANK do the
elimination.** Which is exactly what D30 §1 always claimed rank was for, and
which the author had talked himself out of two messages earlier.

### And it dissolves M3's finding instead of repairing it

R11/M3 measured "20 of 22 rows have completely unconstrained rank" and I read it
as a hole for two sessions. Under the local-tiebreak framing it is not: rank only
means something between CLASHING rows, so the 20 are rows whose value genuinely
does not matter. What is constrained is what needs to be, and the per-row
`syntax` check does it for free.

### Rank vs order is settled by measurement, not preference

Order was proposed and is refuted on the shipped table with no edit: the
tail-less `\N` is declared FIRST (`registry.c:242`) so first-match claims
`\N{U+0041}` (16/17 probes), and pinned last, `"{"` still precedes `"{U+"`
(7/17). And the irony is exact — those rows are shortest-first DELIBERATELY so
`check_tail_precedence` would have a pair to observe. The decisive property is
blast radius: 4 of 96 adjacent swaps are load-bearing, but **520 of 2,308
arbitrary swaps**, because moving an unrelated row across a bucket's span
corrupts that bucket as a side effect of where it LANDS. Rank travels with the
row; order is a property of the file.

### D30 §6 is dropped, and the reason is structural

Frank's point: a parser-continuation function has the intermediate data already
built, so it knows the running capture count and simply decides whether `\12` is
octal or a backreference. D30 deferred that to the semantic port to preserve
PURITY — and that trade was bad because **purity was made GLOBAL when it is
needed at exactly ONE doorway**. The class doorway needs a pure decide phase for
its predicate; the escape doorway needs the count; they are different doorways
and never conflict.

Measured while checking it: `\8` followed by EIGHT groups compiles, seven does
not — so `\1..\9` uses the WHOLE-PATTERN count, a forward reference no
already-built state reaches. **Two counters are owed, not one.** `[MOD-STATE]`
still owns the second.

### Recorded in D32 §8 so they are not re-proposed

Trial mode (refuted by building it), declaration order, the two-port split with
`head_len`, one-function-per-bucket (the author's synthesis, made unnecessary),
and disjoint-forms-without-rank (the author's, and worse).

**Five of the author's claims were refuted across R12 and three more in
conversation.** The pattern worth keeping: Frank's corrections came from
questioning a premise the panels had inherited, not from finding an error in
their work — every panel was internally sound and built on the same unexamined
assumption.

## 2026-08-11 — SESSION CLOSE

A long session. **Two steps of real work, three design panels, and one design
resolved after three attempts.** Everything committed and pushed.

### Delivered

**[PARSE-1] — built, checked, committed** (`0ebbdc7` + `5d4663f`). `p_alt`
reports `AltInfo {nbr, last_bar}`; the group case split into
`p_group`/`p_group_body` so entry and exit bookkeeping sit on one path each;
`caseless` moved from the const caller-owned options into `Ctx` and
saved/restored at the group boundary; `pcrec_parse_body` added as the actual
module callback. New suite `tests/parse/`, 8 checks, every one
sabotage-verified.

**[MOD-0.1] — UNBLOCKED by D32** after R11 refuted D30 and R12 refuted the
alternative. Nothing built; the interface is now specified.

**K11 recorded** — `pcrec_ext_escape`'s two call sites are UB the moment that
doorway returns; `[a\qb]` SIGSEGVs the compiler itself in a stub build.

### State at close

    make test  EXIT=0, 0 FAIL: unanchored
               1012 / 85 / 397 / 164 / 143 / [parse 2+8] / 29 / 7
    make strict  clean
    verify_rxt   980 PASS / 0 FAIL (100%)
    fuzz seed 1  zero divergences
    make bench   0 hard errors, 0 budget failures  (needs TMPDIR=/var/tmp)

Nothing in `STATE:started` except `[MOD-0]`. `[PARSE-1]` completed,
`[MOD-0.1]` not-started and unblocked. Open defects: K2, K7, K9, K10, K11.

### What this session actually cost, and where the value was

**Almost none of the value was code.** It was: three retractions of the author's
own claims caught by measurement (the bench-(d) trie regression, "`make bench`
measures throughput", the `find()` tie-break); one real miss caught after a
commit (`p_alt` had no linkage, which was PARSE-1's entire stated purpose); a
panel that stopped MOD-0.1 being built against a specification its own
measurements contradicted; and a design resolved by Frank questioning a premise
three panels had inherited.

**The process failures are the durable output.** Recorded in R11, R12 and here:

1. **A checkpoint is not closed when the build is green.** Panels delivered
   after the commit THREE times, once after a push. `ListAgents` reported no
   reachable agents while five still had output. An agent-list check is
   EVIDENCE, not proof — the real protection is that a follow-up commit is cheap
   and normal.
2. **Narrow briefs beat broad ones, measured twice.** R11 ran 2-of-4 with
   five-part briefs; R12 ran 4-of-4 with one primary question each.
3. **Hand-listing an input space fails silently.** R11's escape alphabet omitted
   all 11 letters that would have exposed a hole in its own criterion — the
   published numbers were unchanged only by luck.
4. **A design that cannot be run should be SIMULATED against the real data
   before adoption.** D30's rank was, and survived. The ordered-list design was
   not, and died on the shipped table with no edit required.

### Next session

Per Frank: **discuss the remaining open issues and update the docs, THEN run a
critic review.** Not building MOD-0.1 first. The open list is in wake.md §6 and
D32's "still owed" — the residue check's fourth category, the whole-pattern
capture count, the four returning-doorway call sites, two missing doorway
epilogues, K2/K7/K9/K10/K11, the bound compile mode's contents, and a UBSan
build.

## 2026-08-11 — THIRD session of the day: open-issues discussion, and D33

Per Frank's instruction at the close of the previous session — *"discuss any
other open issues and update then critic review"*. No building. The review is
still owed at the time of writing.

### Baseline, verified before anything else

    make            exit 0
    make test       exit 0, 0 "FAIL:" counted UNANCHORED
                    1012 corpus / 85 CLI / 397 reject / 164 registry / 143 PC-3
                    / 2 + 8 parse / 29 codegen / 7 trie-identity
                    known-fail ratchet empty
    make strict     exit 0 — whole tree clean under -Werror
    verify_rxt.py   980 PASS / 0 FAIL (100%)
    fuzz --seed 1   0 content divergences, 0 accept/reject divergences,
                    12 DFA state-cap hits (the known M4 limitation)

`make bench` NOT run: nothing since the last green run touches codegen, and it
is the one gate that costs real time and disk. Stated rather than skipped
silently.

### Decisions taken (Frank)

- **K2** — backrefs and octals get their OWN parser functions, rather than one
  hedged row. The clash is multi-digit only; a single digit is never octal and
  `\0` is never a backreference (measured below), so the two functions are
  disjoint except over `\dd+`, where the RUNNING capture count decides. Rank
  cannot be the tiebreak there — rank is static and that answer is dynamic —
  which D32 §2 does not spell out.
- **K9** stays with DD-3. **K10** stays with MOD-0.6 (the entry is right that
  fixing the flag without the in-class tail sweep leaves the same four blind
  nets) and remains a known issue regardless of where it is scheduled.
- **The unguarded `unknown escape \%c` diagnostics** (`ext.c:84-85`) are to be
  pinned. NOT YET DONE at the time of this entry.
- **The reachability differential's fourth residue category** goes to the panel
  as one critic's single primary question rather than being decided at the desk.
- **D33 written** — see below.

### D33: one table, two ports

Frank's design, arrived at by questioning a premise I had inherited from D32.
One row per construct carrying TWO function references — a class port returning
a set, an AST port returning a node — with the AST port of every class-shaped
row being ONE shared generic wrapper, because `char_node` already normalises
literals to singleton `A_CLASS` nodes and codegen emits membership tests from
`cls[32]`. For the ten character-type escapes the class port is DATA (a bitmap
plus a negate flag), not a function.

Two separate tables were considered and rejected: their overlap is exactly the
escape doorway's class-shaped rows, which is where K10 lives, and splitting them
turns one self-contradicting row into two rows nothing forces to agree.

### THREE of my own claims were refuted in this session, all by Frank

1. **"Schedule `[MOD-STATE]` as a real step now; it gates K2."** Wrong on both
   counts. Measured it after saying it: `[MOD-STATE]` owes TWO counters and only
   the RUNNING one is on MOD-0.1's path. The whole-pattern count decides
   VALIDITY (`reference to non-existent subpattern`), which pcrec never says,
   because it refuses every `\1..\9` with "requires module" first. So it is owed
   to whoever IMPLEMENTS `backrefs`, not to the dispatch work. The real defect
   is smaller and different: `[MOD-STATE]` is a name in prose with no plan entry.
2. **"`pcrec_ext_class_pair_opens` is irreducible."** I argued a speculative
   predicate was structurally necessary, because at an endpoint PCRE2's
   "invalid range" beats the construct's own diagnostic and parsing it first
   loses the right answer. That is true ONLY because `ctx_fail` longjmps — the
   construct's error escapes before the caller can override it. Frank's "the
   class parse code could call the class table freely, as it will either return
   a class or not" dissolves it: once a claim is a RETURNED value, the endpoint
   caller sees the claim first. All ten measured cases then fall out of one rule.
   **I had reasoned from the implementation's control flow and called the result
   a structural necessity.**
3. **"The payload split is `Ast *` vs `int`."** That is the base-tier picture
   only. Every module that makes doorway 1 return at class position contributes
   a SET (`\d`, `\v`, `\p{L}`), which an `int` cannot express — so the class
   payload has to be rewritten whether or not the accessor is unified, and my
   objection to unification was weaker than I stated.

And one I nearly got wrong while writing D33 §4: I first wrote the arbitration
as "filter to rows with a class port, then rank". Measured, it must be
"arbitrate as today, THEN consult the winner's port" — the other reading makes
`[\N]` answer `\N{name}`'s error.

### Measurements taken this session, with method

All against libpcre2 10.46 through `tests/fuzz/pcre2_abi.h` (this box has the
runtime but not the -dev package: no `pcre2.h`, no `-lpcre2-8`), probes written
in the session scratchpad, never in the repo.

**The whole-pattern capture count, reproducing D32 §5 independently:**

    \8 + 8 groups  COMPILES      \8 + 7 groups  err 115
    \1             err 115       \1(a)          COMPILES   <- pure forward reference
    \3(a)(a)(a)    COMPILES      \3(a)(a)       err 115
    \12  COMPILES   (a)\12  COMPILES   \0  COMPILES   \012  COMPILES

`\1(a)` is the sharper form than the `\8` pair, and single digits are never
octal — `\1` is 115, not `\001`.

**Range endpoints — the rule is the row's SHAPE, not the doorway:**

    [a-\d] [\d-x] [a-\v] [\w-z] [\d-\w]   err 150 invalid range
    [\d]                                  COMPILES (member, not endpoint)
    [\x41-z]  COMPILES     [a-\x41] [a-\n]  err 108 out of order (i.e. a RANGE)

**Position beats name validity for brackets, and does NOT for escapes** — this
asymmetry is what made a speculative predicate look necessary:

    [0-[:foo:]] err 150   vs   [[:foo:]] err 130 unknown POSIX class name
    [0-[.ab.]]  err 150   vs   [[.ab.]]  err 113 collating not supported
    [0-[=x=]]   err 150   vs   [[=x=]]   err 113
    [0-\q]      err 103 — the ESCAPE's own error wins
    [0-\N{U+41}] err 193 — the construct's own MODE error wins (scalar-shaped)
    [0-[a]  [0-[:]  [0-[:digit]  [0-[.]   COMPILE — no pair closes

`ext.c:344-349` already recorded "position beats name validity"; this reproduced
it rather than found it.

**The class-position port map, which forced D33 §3:**

    [\A] [\Z] [\K] [\R] [\X]  err 107 escape sequence is invalid in class
    [\N]                      err 171 \N is not supported in a class
    [\N{name}]                err 137 — SAME answer as outside a class
    [\N{U+41}]                err 193 — SAME answer as outside a class
    [\b]                      COMPILES — backspace, BASE syntax

`ESC_CLASS_BASE` (1 row, `\b`) and `ESC_CLASS_INVALID` (10 rows) both mean "the
class doorway is not taken" for OPPOSITE reasons, so a NULL port cannot say
both. Making `\b`'s class port return `EXT_SCALAR 0x08` disambiguates it and
deletes both flags plus `parse.c:152`.

**Counted, not estimated:**

    ctx_fail sites in src/   50 total — 23 in ext.c, 20 in parse.c, 4 in compile.c
    row-macro invocations    97 (+3 raw struct literals = 100 rows)
                             ESC 18, ESC_CLASS_INVALID 10, ESC_DIGIT 10,
                             GROUP 24, GROUP_OPT 12, GROUP_T 16, others 7

The 23 is the deferred-diagnostic blast radius, and it is one file, not the tree.

### K12 recorded

`[0-\d]` is answered "requires module 'classes'" where PCRE2 says err 150,
invalid range — permanently. SPEC-FA implemented the endpoint rule for the
BRACKET shape only. Not a miscompile (both engines reject), but pcrec is right
today only because `\d` is refused before `parse.c:213`'s range code can see it:
**the guard is the unimplemented-ness, and MOD-0.2 removes it.** Same shape
`docs/plan.md:577` already records for `(?xx)[a- ]`, one construct over.

### Next

The critic review is still owed, and D33 §5 names its own primary target: the
deferred diagnostic. If a diagnostic cannot cleanly outlive its handler,
`pair_opens` returns and D33 §6 collapses.

## 2026-08-11 — same session, continued: the extension design and R13

Frank's instruction, given mid-session: write the extension mechanism up as its
own design document from scratch (not as an amendment), self-review it, send it
to critics with different lenses, apply what I agree with strongly, leave the
rest open, then close out. He went AFK partway through; the rest was carried out
against that instruction.

### Two new ideas from Frank, and what they turned out to be worth

**1. "The interface to the class handler could be different — you could send
special instructions."** This dissolved the problem I had told him was
structural. I had argued `pcrec_ext_class_pair_opens` was irreducible, because
at a range endpoint PCRE2's "invalid range" beats the construct's own diagnostic
and parsing it first loses the right answer. That is true ONLY because
`ctx_fail` longjmps. An explicit ASK level lets the caller ask "do you claim,
and what shape" without the construct's error escaping. **I had reasoned from
the implementation's control flow and called the result a structural necessity.**

**2. "A name associated with each row or logical grouping of rows, used to turn
handler sets on and off dynamically."** Measured while writing it up: **the names
already exist and are half-built.** `FEAT_*` is a 16-bit mask in
`internal.h:219-234`, `RegRow` carries `unsigned feature`, and
`registry.c:129-144` pairs each with a string. 100 rows, 16 features, every row
carrying exactly one bit or zero, `classes` spanning 3 buckets and `backrefs` 2.
Nothing uses it beyond printing a module name.

And three separate open issues turned out to be one hole: `\U`, `\u`, `\F`,
`\L`, `\l` have NO REGISTRY ROW, so they fall through to `ext.c:84-85`'s generic
`"unknown escape \%c"` — which is simultaneously the project's only completely
unguarded diagnostic surface (R11 disposition 14), D32 §9.4's missing fourth
residue category (46 of 93, 49%), and the reason D30 §4's bound-mode list could
not be written.

### R13 — five lenses, and the design was partly refuted

Full report: `docs/reviews/2026-08-11-r13-extension-design.md`. Roughly 61
findings over ~3,370 lines. **Eight load-bearing claims fell, four of them to
independent measurement by more than one critic.**

The four independently-reached refutations:

1. **Selection is NOT position-independent** (four critics). `(a)x12\12` is a
   backreference; `(a)x12[\12]` is still OCTAL, at the same capture count.
   C3 widened it to 114 of 168 cells. **And the methodological lesson is
   sharper than the finding: my evidence was three `\N` probes, all REFUSALS at
   class position, so the two competing readings were indistinguishable on that
   data. I measured the claim on the only bucket that could not test it.**
2. **`\Q...\E` is representable by nothing in the design** (four critics), and
   the natural reading is a tier-1 miscompile — `^\Qab\E*$` matches "abbb" and
   NOT "ababab", because a quantifier binds the last character of a quoted run.
3. **The endpoint rule is decided by the DOORWAY, not a shape column.**
   `[0-\p{Foo}]` is 147, not 150. My justifying contrast varied two things at
   once and credited the wrong one.
4. **`\b`'s two facets have different owners** — I found this half myself before
   the panel and got it half right; C5 found the miscompiling half I missed
   (the shared generic wrapper makes `a\bb` compile to `a\x08b`).

**The single most useful finding (C2/F3):** my document condemns "the guard is
the unimplemented-ness" twice — at K12, and by citing `plan.md:577` — and then
commits the identical error defending the whole-pattern pre-scan. Measured:
`\1(?n)(a)`, `\1(?#()`, `\1\Q(a)\E` are all err 115, so `\1`'s validity at
offset 0 depends on constructs owned by four other features appearing later.
Being able to name a failure mode twice in a document and then commit it in the
same document is worth more than the finding.

### K13 recorded — a live shipped bug, reproduced before recording

Twelve rows (the ten digit rows plus `\g` and `\k`) answer the CLASS position
with module `backrefs` for constructs it can never implement. Verified by the
author against libpcre2 10.46, not taken from the panel:

    [\8]   matches "8" — the LITERAL character
    [\1]   matches "\001" — OCTAL
    [\k]   matches "k", not "\"       [\g] matches "g"
    [0-\k] a legal RANGE 0x30..0x6b

pcrec answers all six "requires module 'backrefs'". Over-promise today; a
tier-1 miscompile the day `backrefs` lands, arriving BECAUSE the module was
implemented. Every net misses it for K10's reasons, including the same one-byte
`"[\\%c]"` sweep template.

### The checks did worst of all

C4: 26 findings against ten checks. Check 4 is vacuous for ~90 of 100 rows —
most rows' recogniser IS "compare the first byte to `row->sel`", so asking that
function whether it returns NOT_MINE when the byte differs from `row->sel` is
its own definition evaluated ninety times. And check 4's SCOPE is the field it
validates: `RK_VERB` has exactly one row and it is `REG_SEL_ANY`, so that
bucket's coverage is permanently zero. Both are the K10 shape my own document
cites as its template.

**Disposition: §8 gets rebuilt by someone denied the design's reasoning.** The
density of scope-inheritance defects across ten checks is the signature of one
author writing both a mechanism and its controls — which is what D27 exists to
break, and this is the second measurement that it works.

### Negative results worth not re-deriving

- **`unicode-props` / `classes` coupling is exactly ZERO** (8,716,400 compile
  pairs). My own [OPEN] question named the wrong pair.
- **`PCRE2_UTF` changes 0 of 120,099 verdicts**, reproducing R10 with a
  different generator.
- **At the class-bracket doorway the endpoint rule is EXACTLY right** — 21,396
  patterns, zero disagreements. The defect is the generalisation to the escape
  doorway, not SPEC-FA's rule.
- **`\x` is mode-dependent under ALT_BSUX** — a BASE-GRAMMAR escape, so the
  mode-dependent set reaches into the base grammar. New information; the design
  had two categories and there are three.

### Process

- **Second prods delivered most of the panel, again.** C4 168 → 1003 lines,
  C5 87 → 721, C2 57 → 454. The first round is not the panel; budget two.
- **C2 caught its own control error mid-flight** (`(?:)` conflates
  quantifiability with state-setting; `(?i)` does not) and re-ran 8.7M pairs.
- **C2 and C4 established PCRE2 option bits behaviourally** rather than looking
  them up — sweeping all 32 single-bit options and disambiguating `ALT_BSUX`
  from `PCRE2_LITERAL` with a second probe.
- **My own review pass found two of the eight refutations** and got one only
  half right. Worth doing; not a substitute for the panel.

### State at close

Baseline verified green at the top of the session and NOT re-run after these
changes, because everything since is documentation — no source file was touched.

    make / make test   exit 0, 0 FAIL: unanchored
                       1012 / 85 / 397 / 164 / 143 / 2+8 / 29 / 7
    make strict        clean       verify_rxt 980/980
    fuzz seed 1        0 divergences

Open defects: K2, K7, K9, K10, K11, K12, K13.

### Still owed, and deliberately not done

**A1 — pinning `ext.c:84-85`'s two unguarded diagnostics — is NOT done.** Frank
approved it earlier in the session. It was held back because the design's §7.1
proposes giving those five escapes ROWS, which changes the wording, and because
the critics were reading the tree. It should be the first thing built next
session, and the pin is now MORE valuable than when it was approved, because it
makes §7.1's change visible.

The D-group items Frank has not ruled on: the bound compile mode's list (which
§7 now has most of the material for) and a `make ubsan` build.

### ADDENDUM, same day — material delivered AFTER the commit, and it corrects a COMMITTED finding

**The R11 rule fired for the third session running.** Immediately after
committing `ce506af`, `ListAgents` reported "No reachable agents" while three
critics went on to deliver another ~1,000 lines: C1 583 → 1031, C5 721 → 1126,
C2 454 → 643. The agent list is evidence, not proof. Follow-up commit made, as
the discipline says it should be.

**`PCRE2_UTF` DOES flip a construct verdict, refuting R10 as recorded in
D30 §4.** Verified by the author, UTF bit established behaviourally (bit 19 —
the bit that makes `\xff` raise "UTF-8 error: illegal byte"):

    \N{U+0041}     opt=0  err 193      opt=UTF  COMPILES
    [\N{U+0041}]   opt=0  err 193      opt=UTF  COMPILES

It is **K10's own construct**, the row used as the worked example in D32, D33
and the extension design. And the registry's own `note` on that row already said
*"PCRE2 error 193 outside UTF mode, which is recognition, not rejection"* — the
table knew what the measurement denied. Two homes for one fact, one wrong.
D30 §4 now carries the correction inline.

**The method lesson is bigger than the correction, and it is the SECOND
instance in one session.** C2 measured `PCRE2_UTF` as changing 0 of 120,099
verdicts and was RIGHT — its probe space was strings of length 1..3, which
cannot contain a ten-character construct. C5 swept the registry's own `syntax`
strings, which can.

> **Counting a population by a generator that cannot produce it counts the
> generator.** Two correct sweeps, opposite conclusions, and the whole
> difference is which family the generator could express.

That is the same failure as the design's position-independence claim being
evidenced on the only bucket that could not falsify it. Twice in one session,
from two directions. The existing lesson — "GENERATE the input space, never list
it" — is not sufficient; a generated space can be just as blind as a listed one.

C5's full sweep found **8 verdict-changing option bits, not two** (`ALLOW_EMPTY_CLASS`,
`ALT_BSUX`, `NO_AUTO_CAPTURE` 11 flips, `UTF`, `NEVER_BACKSLASH_C`, `LITERAL`
143, `MATCH_INVALID_UTF`, `ALT_EXTENDED_CLASS`); the other 24 flip nothing. The
rest of R10's "flips nothing" list is not disturbed, but it came from the same
method and should be re-swept over a space that can express multi-character
constructs before it is relied on again.

**And it breaks §7's framing rather than just its list:** `\x` is mode-dependent
under ALT_BSUX and is BASE grammar — pcrec implements `\x41` in `parse.c`, not
in the table — so `\x` must not get a row, and the bound compile mode is not
expressible as a set of row statuses or names.

Three critics independently reached K13 (C3/F6, C4/F21, C1/F9); C1 added
`[\k<name>]`, `[\g{1}]` and `[\9]`. K13 was written before that material
arrived and needs no change.

### ADDENDUM 2 — the panel IDLED, and the last pass found a second live defect

All five critics idled 08:18–08:29; the 08:33 re-poll matched. **First
checkpoint in three sessions to actually reach the "every critic has IDLED"
bar before closing** rather than inferring it from a quiet agent list.

Two items had been read only as headings when addendum 1 was written.

**K14 recorded — a second shipped tier-2 defect, verified on all three legs.**
pcrec names a module for constructs its own compliance survey calls
architecturally out of scope:

    (*COMMIT) (*PRUNE) (*SKIP) (*MARK:x)  ->  "requires module 'verbs'"
    \d                                    ->  "requires module 'classes'"  (PLANNED)

Indistinguishable to a caller, opposite promises. `decisions.md:1457` carries
D26's wording — *"Naming a module that will never implement a construct is a
defect"* — and `pcre2_compliance.md:301` already says the backtracking verbs
are excluded because "a simulation engine explores all alternatives at once, so
there is no backtracking tree to prune". **The fact is written down correctly
and contradicted by the diagnostic.** Two homes, one wrong — the shape the
single table exists to prevent, found in the docs rather than the table.

**And the missing distinction is an AXIS, not a status.** What pcrec will EVER
do is a fact about pcrec's roadmap: not about PCRE2, so the status column cannot
hold it; not about one compile, so the enabled set cannot hold it. The design's
`RS_NOT_OFFERED` and its permanently-disabled-name alternative are BOTH category
errors — which retires §10's open question 1 as posed instead of answering it.

**C1 produced a repair, which is the panel's best constructive output.** Asked
for an alternative rather than only a refutation, it diagnosed the ASK contract
correctly in a way I had missed: the three levels are a TOTAL ORDER over one
axis when the measurements describe TWO. `(?(` needs the least information and
the most effects, so it is simultaneously the highest and lowest rung. Its
re-cut — `want` (CLAIM/VERDICT/RESULT) crossed with `may` (a capability set) —
makes the missing point expressible, and it is distinguishable from D32 §8's
refuted trial mode because allocation is permitted rather than trapped.
**Recorded, NOT adopted**: adopting an unreviewed design at the desk is exactly
what this panel caught me doing.

**Obligation C, counted from git rather than argued** (C5/F12): the cleanest
single-construct addition in the repo's history costs **four files and six
edits** — the row, one reject-manifest assertion, and four hard-coded totals.
"Adding a row and nothing else" is already false by a factor of six, and the
design removes none of the six.

Open defects now: K2, K7, K9, K10, K11, K12, K13, K14 — and K12/K13/K14 are the
same shape three times over.

## 2026-08-11 — FOURTH session of the day: Frank's rulings, Part II, R14, A1

Frank reviewed the design document, agreed with the recommendations on every
open question, asked one question of his own — is `\Q\E` lexical enough to be
core grammar? — and asked for the design passes. What happened, in order:

**Baseline: green, after an environmental fight.** `/tmp`'s per-user tmpfs
quota was exhausted by 5.5 GB of PRIOR sessions' scratchpads — exactly what
wake.md §3 warned about — which broke `make test` mid-run (gcc could not
write its own temp files) and briefly broke the shell itself. The permission
layer declined a bulk delete of the stale scratchpads, so everything this
session ran with `TMPDIR=/var/tmp`, and the cleanup is flagged for Frank to
do by hand. All six baseline gates then passed: make, make test, strict,
verify_rxt (100%), fuzz seed 1 (0 divergences), bench (0 hard errors, 0
budget failures — the real run, not the quota lie).

**Measurements first.** Two probe programs against libpcre2 10.46 before any
design prose: 24 `\Q\E`/`(?#)` lexical cells, the full 62-escape class-
position sweep (the literal-fallback set is exactly `\g \k \8 \9`), the
endpoint doorway×side table, the atom-side digit facts, and re-verification
of every C2/F3 forward-reference cell. The `\Q\E` answer to Frank: lexical
YES (every cell consistent with a tokenizer mode; quantifier binds the last
character, ranges form through `\Q\E` and bare `\E`, case-folding applies
inside, `(?x)` suspends and resumes), core grammar NO (pcrec refuses all
three today with module names; D26 tier 2 needs the attribution; the
sabotage instrument needs the toggle) — implementation locus and gating are
different axes.

**Part II written (§11-§17), D34 recorded, then R14 the same session.**
Three read-only critics (measurement / coherence / controls), ~5,400 probes.
The panel refuted Part II's two central factual claims and it was RIGHT both
times — every load-bearing measurement re-verified by hand before applying
(29-cell verification probe, all reproduced):

- §16.2's "exactly ONE deviating cell" — there are TWO (`[:<:]`/`[:>:]` are
  whole-class-content assertions, low-side 130), and the falsifying cell was
  printed in §16.1's OWN TABLE and read as confirmation. Plus a FIVE-step
  evaluation order the 33 curated cells were structurally blind to (every
  cell had a literal on the non-construct side). C1's 5,041-pair generated
  differential — predictor fed from libpcre2, never from the row — found 71
  disagreements, all one item, and nothing else.
- §14.2's digit rule — `\81` is err 115 at ANY count: a run beginning 8/9 is
  always a backreference. Derived from `\12`/`\8`/`\0`, a probe set with no
  run beginning 8 or 9. THE method failure, committed while correcting it.
- "backrefs can land alone" WITHDRAWN: the count-scan must classify every
  `(`-form (named groups capture; `(?<n>` vs `(?<=`), needs verb/callout
  body extents (two ROADMAP_NEVER families), and `(?|` needs the
  nesting-aware top-level `|` scan R13 used to kill TERMINAL — "that scan IS
  the parser" came back through the side door. Migration order is now
  Frank's decision (§18.1).
- Quote mode is scoped to ATOM/CLASS-ITEM positions — `(\Q?\E:a)` is a
  CAPTURING group. §13's tokenizer story holds exactly where it was
  measured (34/34) and nowhere else.
- Quantifiability is a THIRD per-row axis nobody modelled: `a\b*`,
  `a(?i)*`, `a(*FAIL)*` are all err 109, and an EXT_NODE from any of the
  22+ non-repeatable rows lets try_quant compile them — R13's `\Qab\E*`
  mechanism, generalised. New `quantifiable` fact, external sweep.
- Three critics independently saved `pcrec_ext_class_pair_opens` from
  deletion — the "two-byte lexical test" that replaced it over-rejects the
  four accept-controls D33 §9.1 calls mandatory. Deleting the thing measured
  (21,396/0) while keeping its measurement was the design's clearest error.
- C3 on the first §17.3: six of nine invariants could not fail in the
  direction the design's own gaps produce ("an invariant with no population,
  no oracle and no sabotage is not a weaker check — it is a sentence").
  Rebuilt: every entry now names oracle, population, sabotage.

All corrections applied inline as R14 blocks; §18 is the post-R14 state and
Frank's five open decisions (migration order; does `may` survive now that
`(?(` uses the scan; where `quantifiable`/`captures` live; K13-fix
sequencing vs the byte-identity bar; the bound-mode document's scope).
Review compiled at docs/reviews/2026-08-11-r14-part2.md. D33 got its
amendment banner (its own revisit-when had fired unmarked — C2/F13).

**A1 landed.** Ten `unknown escape` pins for `\U \u \F \L \l` (atom + class)
in tests/reject/, count 235→245, one manifest entry — sabotage verified live
(deleting the rows fails the MANIFEST by name, not a count). Full `make
test` green after.

**Lessons, added to the pile:**
- A CURATED TABLE CAN CONTAIN ITS OWN REFUTATION AND STILL CONFIRM THE RULE
  TO ITS AUTHOR. `[[:<:]-z] 130` sat in §16.1 while §16.2 said "every cell
  above follows". Reading a table you built checks transcription, not the
  rule; only a predictor fed from the oracle checks the rule.
- THE FIX FOR "MEASURED ON A BUCKET THAT CANNOT FALSIFY" IS STRUCTURAL, NOT
  VIGILANCE: generate the probe set from the claim's failure directions
  (both-sides-construct pairs; digit runs starting 8/9; quote at non-atom
  positions). Three instances in two days of the vigilance version failing.
- A PANEL THE SAME SESSION IS CHEAP AND THE DESK IS EXPENSIVE. Part II was
  written carefully, from fresh measurements, by an author who had just
  catalogued R13's failure modes — and still shipped two false central
  claims that three critics found in under an hour.

**Next session:** Frank answers §18's five decisions. Then the plan. The
checks (§17.3) go to a D27 author with probes, not prose. Do not start
building before the §18 conversation.

## 2026-08-11 — FIFTH session of the day: §18 resolved, the plan built

The design conversation, completed. Frank ruled on all five §18 decisions,
and two of his questions materially changed the design before it reached the
plan:

**"I recall you arguing against a scanner" — and the scanner died.** The
original anti-pre-scan argument was right all along: eighteen targeted probes
plus a 2,931-probe generated sweep (predictor stated first, backref-ness read
via PCRE2_INFO_BACKREFMAX, zero disagreements) established that multi-digit
octal-vs-backref uses the RUNNING count (`^\12(a)x12$` is octal — the total
is irrelevant), the total count is validity-only, and PCRE2 reports every
structural error before err 115 — which is exactly what deferred end-of-parse
resolution produces by construction. Running count in `Ctx` + a
pending-references list + one end-of-parse check, all in the real parser.
"backrefs can land alone" is TRUE again. plan.md's [MOD-STATE] note had
recorded the running/validity split all along; Part II walked past a fact the
repo already held.

**"Is a row always deterministically quantifiable?" — no, and the question
caught my fresh overclaim.** Twenty-six probes: the option-run rows span both
values BY FORM (`a(?i)*` 109, `a(?i:b)*` compiles) and the verb row spans
both BY NAME (`a(*FAIL)*` 109, `a(*pla:b)*` compiles — and it is not the
colon boundary, `(*MARK:x)` is 109). Two turns earlier I had told Frank the
verb row was uniformly non-repeatable, from C3's two probes. The column is
three-valued with two form-resolved spans; the verb value lives per-VerbName
on the K14 machinery.

**The other rulings:** leftmost-refusal policy for disabled `(?(` ("this is
not an exercise in emulating the exact interface of pcre2") — `may`
collapsed, exact E127/E154 moved to the conditionals landing bar, third
policy witness pinned in tests/reject/ (245→246, manifest entry, green);
K13 fix lands FIRST as [FIX-3], pre-mechanism; the bound-mode document
deferred with one constraint (before §7.1's rows).

**The plan:** MOD-0's pre-existing substeps (.1-.8, D30/D32-era — which I
initially missed and briefly duplicated before reconciling) now carry a
fifth-session preamble listing the known conflicts with the resolved design
(pair_opens survives, check (c) refuted, digit model superseded, per-port
recognition) and MOD-0.1's additional scope. New steps: [FIX-3] (K13, first),
[SPEC-MOD0] (the §17.3 checks by a D27 author, handed tests/probes/ — the
six probe programs are now committed there with a CLAUDE.md stating the
predictor-from-the-oracle method), [DOC-BM] (deferred). Execution order:
FIX-3 → MOD-0.1 + SPEC-MOD0 → .3 classes → .5 modifiers → .4 verbs →
.6 unicode-props → .7/.8; backrefs and conditionals are post-MOD-0.

**Also this session:** /tmp unclogged (Frank ran the cleanup; 5.5 GB freed,
13% used — TMPDIR=/var/tmp no longer needed but harmless).

**Lesson:** BOTH design-changing facts this session came from Frank asking a
one-line question about something the design asserted. The panels missed the
scanner's needlessness and the quantifiability spans; the questions "do we
really need this?" and "is this really constant?" found them in minutes. Ask
those two questions of every new mechanism and every new column, before the
panel does.

**Next session:** implement FIX-3 (the twelve literal fallbacks, oracle
pins first), then start MOD-0.1 and spawn SPEC-MOD0.

## 2026-08-11 — fifth session close-out

Frank's directive for the next session: **development starts.** Work through
several plan sections, not one — using subagents (lesser models where the
work fits one, per D5), and running MULTIPLE subagents in parallel on
NON-DEPENDENT sections. The dependency spine stays serial (FIX-3 gates
MOD-0.1's byte-identity bar), but SPEC-MOD0 is parallel BY DESIGN (its
author must not see the design document anyway), and the plan carries
several sections with no edge into MOD-0 at all (TS-2/3/4 concurrency tests,
MECH-1/2/3 tooling, the R3.6-R3.10 bench-gate repairs) that can run
alongside. Wake.md §1 carries the orchestration sketch. Session closed with
a clean tree at a0eb618 + this entry.

## 2026-08-11 — SIXTH session: dev starts. FIX-3 + K14 landed; four parallel tracks reviewed in

Frank's directive executed: the spine ran serial, four subagent tracks ran in
parallel (briefs restated the scope mandate, banned `make` in the main tree,
partitioned by directory), and everything that landed was reviewed first.
Baseline verified green before any change (all six gates, FAIL: counted
unanchored, fuzz 0 divergences).

**[FIX-3] / K13 CLOSED — first src/ change of the module era** (commit
1b83fbc). The §18.4 loop exactly: probe first (tests/probes/probe_fix3.c, 43
cells, predictor stated in the header before the run, zero disagreements
with libpcre2 10.46), oracle-verified pins first
(tests/base/class_escape_fallbacks.rxt, 127 cases, 122 watched failing),
then ~15 lines in esc_class_value — [\0..\7] octal (≤3 digits, >\377 = PCRE2
error 151 with wording AND offset), [\8] [\9] [\g] [\k] literal, tails
re-enter, endpoints ride with no extra code — plus RF_CLASS_BASE on the
twelve rows. Reject table +2/+1 (the error-151 boundary, both sides), counts
248/63. Byte-identity vs pre-fix HEAD: 328/328 identical, exactly the 38 pin
patterns newly accepted, 0 newly rejected. Two corrections to the step's own
text recorded in its STATE block (no twelve reject rows ever existed to
delete; "literals" compressed the octal half). The full suite then caught
registry_check's RF_CLASS_BASE branch over-asserting ([\g{-1}] wrapped in
brackets is an out-of-order range — libpcre2 rejects it too; the derived
check now probes [\<sel>], the flag's actual claim).

**[MOD-0.1] STARTED; slice 1 = the K14 fix, K14 CLOSED** (commit 8e5ab5a).
Roadmap column (PLANNED/NEVER/NONE-unset) on RegRow and VerbName; 17
OUT-OF-SCOPE verb names + the (?C row answer with a no-promise scope
refusal; malformed forms keep PCRE2's own errors. Pins first (14 reject rows
watched failing). §17.2's pairings enforced in registry_check; PC-3 asks
about ATTRIBUTION (two shapes) with which-name-is-which pinned by hand; both
dumps grew a column (13/5 fields, consumers moved). The prose⇔column check
(compliance_section --names, both directions) caught LIMIT_RECURSION missing
from the survey's row ON ITS FIRST RUN.

**Parallel tracks, all four delivered and reviewed:**
- [TS-2]/[TS-3] (commit daf3518): tests/thread/, TSan concurrency over five
  engine shapes + the library built WITH TSan, byte-identity baselines, both
  halves sabotage-validated with planted races. Wired into make test (~7s).
- [MECH-1]+[MECH-2] (same commit): tests/mech/, 20 encoded sabotages, one
  fresh `git archive HEAD` tree each, 20/20 detected; found the trie ".rxt
  corpus" figure stale (2→6) and root-caused the new-wrong-row sabotage's
  0/0→1 (the exact iterated-count tripwire — visible, not fail-proof; SR-4
  blind spot narrowed, not closed). `make mech`; hand tables now point at
  the generator for figures.
- [SPEC-MOD0] (commit this session): tests/spec_mod0/, ten checks, 4 green /
  0 failed / 6 AWAITING-SURFACE (exit 3 ≠ pass ≠ fail, surfaces named BY
  NAME so landing one arms its check with no edit). THREE findings against
  §17.3 as written — the LEXICAL criterion sees two constructs, not three
  (a\Q* swallows its quantifier); endpoint model confirmed 3/200 with the
  extent scan independently re-derived; verb quantifiability is per-NAME
  with a THIRD outcome (26/50 names not askable). Contamination disclosure
  recorded (harness auto-injected two denied CLAUDE.mds; unused).
- [R3.6..R3.10] (commit this session): load re-sampled after measuring
  (INCONCLUSIVE exit 2 per D14), case (i) investigated — 1.94x RUN-TO-RUN
  spread over ten quiet runs, run_history.tsv + rebaseline.sh + EARN=1
  machinery, budgets re-measured on a genuinely quiet box, case (e) now
  exercises the REVERSE skip loop (counted, not timed) with the sabotage
  re-validated at 7.4x. ONE REVIEW CORRECTION: the agent's median floor for
  (i) made the gate flaky (two of its own ten runs sat above the clamped
  threshold; the acceptance run passed by 2.7%) — floor set to the observed
  maximum instead, arithmetic in floors.tsv.

**Lessons:** (1) A derived check asserting a row's syntax in a context the
syntax was not written for over-asserts — [\g{-1}]'s brackets made the check
demand a bug; probe what the flag claims. (2) The gate-side of a re-baseline
needs the FAIL THRESHOLD checked against the recorded run distribution, not
just the center — a median floor under a clamped margin false-fails a
1.94x-noise case. (3) Instrument bugs three times today (stdout .h
collision, basename in emitted #include, wrapper reporting echo's exit) —
each caught by the count-FAIL:-unanchored habit or a differing control.
(4) The prose⇔column check and the MECH-1 matrix each caught a real
discrepancy on their first run — checks that compare two existing homes pay
off immediately.

**Next session:** MOD-0.1 continues. Remaining slices: quantifiable column
(§18.3 + SPEC-MOD0's not-askable third outcome), class_expect column (arms
check04), LEXICAL row kind, want levels + cursor rule, returned-claims
epilogue (K11), endpoint rule (K12), deferred-backref infrastructure. The
six awaiting SPEC-MOD0 checks are the landing bar's instrument panel.

## 2026-08-11 — sixth session, second half: MOD-0.1 slices 1-2 landed

**Slice 2 = the `quantifiable` column** (41a31a1), fed from libpcre2's own
`a<syntax>*` verdicts (my sweep cross-validated SPEC-MOD0's numbers exactly:
68 yes across rows+verbs, 26 not-askable names). Values on every row
(including base — quantifiability is a real fact about supported syntax,
unlike roadmap, and check10 demanded the answer), `form` on the two
measured form-resolved families, `lexical` on {\Q, \E, (?#}; per-VerbName
QuantVerb with the not-askable third outcome. Dumps at 14/6 fields.

**The D27 instrument earned its keep the moment the surface landed:**
check10 caught TWO transcription bugs in my first landing of the column —
`(?>...)` marked `no` (a block-collection artifact in the mechanical
transcription; atomic groups are plainly quantifiable) and the base row
carrying `-`. The spec author's amendment (accepting `lexical` via two
discriminators, then failing a false `yes` on either) went through two
rounds with a ruling in between; their D2 test is the session's cleanest
idea that wasn't mine: **a quantifier with a minimum of zero can only ADD
strings to a language, so a subject accepted without the star and rejected
with it WITNESSES that the star went literal** — no amount of "does it
compile" probing can see that.

**Two D27 process notes, recorded for every future spec-author spawn:**
(1) The harness auto-injects CLAUDE.md/header files into subagent contexts
unrequested — this session it fed the spec author tests/CLAUDE.md,
tests/fuzz/CLAUDE.md, and later src/core/internal.h + src/core/CLAUDE.md,
the last containing `cx->pos` itself. The author disclosed every exposure
unprompted, used none of it (their check06 predates the leak and stands),
and future invariant-6 hardening goes to a FRESH author. The blindness
constraint must be written knowing the harness leaks ambient context.
(2) The author's own sabotage run nearly reported a false clean because
they grepped for `DISAGREE` while the actual failure printed as
`POPULATION ... FAIL` — the vacuity the suite prevents, reappearing in how
its output was READ. Key off exit codes, never a failure-keyword grep.

MOD-0.1 remaining: class_expect column (arms check04), LEXICAL row kind,
returned-claims epilogue (K11), endpoint rule (K12), want levels + cursor
rule (arms check06 via a fresh author), deferred-backref infrastructure
(arms check02), gate/toggles (arms check07/09), enabled-set symbol (arms
check01). Then the byte-identity bar with its guarded exceptions.

## 2026-08-11 — SEVENTH session: MOD-0.1 slices 3-4 (class_expect, LEXICAL kind)

Baseline verified green first (all six gates, FAIL: counted unanchored,
fuzz 0 divergences, bench 0/0 with load 1.20→1.07).

**Slice 3 = the `class_expect` column** (5874b4b). The 15th `--list-syntax`
column: each of the 44 class-reachable rows states what `[<syntax>]` does
under libpcre2 ('err N' / 'char 0xNN' / 'set N'); the 56 group/verb rows
carry an EMPTY field. Measured before transcribed:
tests/probes/probe_class_expect.c re-derived all 44 values and agreed 44/44
with the SPEC-MOD0 pins before registry.c was touched. check04 was armed by
a spec-side subagent DENIED src/ (the check10 spec_col_index pattern;
comparison against the LIVE measured value, not the dump; two exact floors
44/56) — SPEC-MOD0 is now 6 pass / 0 fail / 4 awaiting. registry_check
enforces the 44/56 pairing and the three-form vocabulary; three sabotages
each caught with exactly one named failure, controls green both sides. The
armed check04 verified independently: moved value exit 1, column removed
exit 3, '-' on a group row exit 1.

**Slice 4 = the LEXICAL row kind** (b873c9b). RF_LEXICAL on {\Q, \E, (?#}
per §13.3, rendered in the existing flags column — no new column, no
consumer moves, no behavior change (the three refusal strings verified
byte-exact). The ESC_LEXICAL/GROUP_LEXICAL macros force QF_LEXICAL so the
kind cannot disagree with the measured column; registry_check requires
RF_LEXICAL <=> QF_LEXICAL both directions, watched failing on all three
rows pre-flag.

**Lessons, three instrument incidents in one session:**
(1) `git checkout` as a sabotage-revert REVERTED MY OWN UNCOMMITTED SLICE —
the sabotage battery then measured a tree where the whole column was
missing (44 spurious failures) and the real registry.c edits were lost and
re-applied by hand. Save/restore sabotage state with cp to the scratchpad,
never git, while uncommitted work is in the tree. The tell was failure
COUNTS wildly off the predicted one-per-sabotage.
(2) The byte-identity spot check first reported 10/10 DIFFERENT because the
two sides wrote different basenames and the emitted C embeds the output
basename in its #include — the journal's stdout-.h-collision lesson, met
again from a new direction. Same basename in different directories: 10/10
identical.
(3) A sabotage that moves BOTH homes together (ESC_LEXICAL on \d flips the
flag AND the cell) is invisible to a consistency check by construction —
registry_check's exit 0 there was correct, not a miss; the false CELL is
check10's catch (verified: D1/D2 both false for \d, exit 1). Route each
sabotage to the instrument that owns its failure direction, and expect a
self-consistent forgery to need the ORACLE-side check. Also: check10 takes
three args, and its exit 2 on a missing verbs dump is the harness refusing
to run, not a verdict — key off which exit code, not just nonzero.

**Process note:** make strict caught a missing-field-initializer on the
longhand (?: row that the default -Wall build had scrolled past — strict
after every schema-widening edit, not only at gates. The check04-arming
subagent's report was reviewed as a diff (its edits: the guard, two floors,
the CLAUDE.md row); disclosure requirement was in the brief; no ambient
leak was observed in its delivered work.

**Next:** the returned-claims epilogue (D33 §5, K11) — the load-bearing
slice; then endpoint rule (K12), want+cursor (fresh D27 author for
check06), deferred-backref infra, enabled-set/toggles, the byte-identity
bar.

## 2026-08-11 — seventh session, second half: slice 5 landed (the epilogue); endpoint rule scoped

**Slice 5 = the returned-claims epilogue** (a67058a). D33 §5 as amended:
all four doorways return a tagged ExtResult (EXT_NOT_MINE / EXT_REFUSAL
with the diagnostic formatted at claim time); pcrec_ext_finish is the one
epilogue; parse.c call sites consume the value and end in internal-error
walls. K11 CLOSED — its own stub repro re-run in a scratch tree exits 1
cleanly at both sites (was: silent miscompile at atom, compiler SIGSEGV in
class). The EXT vocabulary is deliberately the exercisable subset;
SCALAR/MEMBERS/NODE arrive with the first producing port, each with a probe
false the day before. Verified by a 952-pattern byte-identity differential
vs the pre-epilogue build (registry probes + corpus + per-doorway byte
sweeps; exit/stdout/stderr/out.c/out.h; sabotage-validated), full suite,
strict, verify_rxt 100%, fuzz seed 1 zero divergences.

**Endpoint rule (K12) scoped before building, recorded so the next session
does not re-derive it.** §16 as R14-corrected: five steps (low's own error
→ high pair-open short-circuit → high's own error → either side SET → 150
→ scalar ordering), two deviating cells ((bracket, high) = pair_opens,
which SURVIVES; (bracket, low) = whole-class-only names, which our
doorway's at-content-start + close-at-]-check already answers). The
composition insight: slice 3's class_expect column IS §16.3(e)'s relocated
shape — the endpoint caller reads the claim (slice 5) plus the row's
measured shape (slice 3). SCOPE JUDGMENT: the override to "invalid range
in character class" applies only where the row's measured value covers
EVERY form reaching it — the ten char-type escapes (\d \D \s \S \w \W \h
\H \v \V; selector = whole construct, no body) and the bracket doorway's
KNOWN POSIX names (the 14-name table validates the body). Body-dependent
rows (\p/\P — no property table until MOD-0.6; \N{U+}, \o, \c — scalar or
err anyway) KEEP the module promise: pcrec cannot certify PCRE2's 150 for
an arbitrary body, answering 150 for [0-\p{Foo}] would be wrong (PCRE2
147), and the promise stays true (the module owns deciding it). The \p
endpoint cells get pins asserting the CURRENT behavior so the boundary is
deliberate, not accidental. All pins failing-then-passing per §17.1's
guarded-divergence rule.

## 2026-08-11 — seventh session, third stretch: slices 6-7 (endpoint rule, capture count); worktree convention

**Slice 6 = the endpoint rule, K12 CLOSED** (f439b95). §16's five steps in
p_class, composed from what the session already built: slice 5's returned
claims make the refusal visible at the range site, slice 3's measured
class_expect column certifies SET-shape (ep_set_certain — §16.3(e)'s
payload, exercisable subset). Certification scoped to all-forms rows; the
\p boundary pinned as deliberate. 42 cells measured first
(probe_endpoint_k12.c, every prediction confirmed), ten
failing-then-passing pins + seven boundary pins + two accept-controls
(counts 265/99/65, three MANIFEST entries), the 952-pattern differential
vs pre-slice HEAD shows exactly the one changed cell it contains.
pair_opens survives as the (bracket, high) deviating cell's predicate,
per R14.

**Slice 7 = the running capture count + its channel, check02 armed**
(this commit). Ctx.ncap at p_group_body's hook (incremented at the
opening paren, so a future \12 consults the right running value);
pcrec_count_groups parse-only entry in compile.c (the file with the
tree's only setjmp); CLI --count-groups with pcrec_compile's exact
refusal behaviour. Oracle-verified 10/10 hand cells + 300/300 generated
base-tier patterns against python re; emitted code byte-identical; cli
case10 85→95. THE PENDING LIST IS DEFERRED to module backrefs by D33
§9.3's own rule — a list nothing can write is unexercised structure;
recorded in plan.md. check02 armed by a spec-side author (denied src/):
runs every generated body through pcrec via execl (no shell), exit 0 →
count must equal CAPTURECOUNT, exit 1 → refused-not-compared. The
honest split today is 1 compared / 101 refused (the families are
count-scan traps, all unimplemented) — both floors pinned EXACTLY, the
compared floor ratchets as modules land. I verified all three directions
myself: control 0, flag-less stand-in exits 3 (awaiting), a lying
wrapper exits 1 naming the body. SPEC-MOD0 is now 7 pass / 0 fail / 3
awaiting (01 isolation, 06 cursor, 07 gate).

**Process changes this stretch:** (1) Frank's worktree ruling — a
subagent that WRITES gets a git worktree under worktrees/ (gitignored,
inside the repo so the scope mandate holds by construction) and delivers
a diff to review-then-merge; critics stay read-only in the main tree.
Recorded in CLAUDE.md. The motivating incident: the check02 author's
edits landed under me mid-review — my background watch fired on the
FIRST file change and I began reviewing a half-delivered state, briefly
misreading missing floors as the author's omission. Worktrees make
delivery atomic. (2) A watch keyed on "any file changed" is not a watch
for "delivery complete" — key hand-off watches on an explicit
done-marker, or use worktrees where the merge IS the marker.

**Next:** want levels + cursor rule (fresh D27 author arms check06),
the enabled-set/toggles surface (checks 01/07/09 — the largest remaining
chunk), then MOD-0.1's byte-identity bar with its guarded exceptions
(K12's ten pins are the exception list's current content, each
failing-then-passing).

## 2026-08-11 — seventh session, addendum: the check02 author's report arrived post-commit

The author's final report reached the main session after its work was
reviewed, independently re-verified, and committed (ec3eaae). It confirms
the review on every point — same files, same 1/101 split (the one compared
body is `(a)(b)`, scoped_n's plain-group control), and its own sabotage B
is the same lying-wrapper test the main session ran independently.

TWO CORRECTIONS TO THE RECORD. (1) The earlier "delivered clean" note is
wrong: the author DISCLOSED a harness leak — the full contents of
tests/CLAUDE.md (a denied path) were auto-injected into its context
unrequested; it reports consuming nothing from it. That is the THIRD
recorded instance of the D27 auto-injection pattern (sixth session:
tests/CLAUDE.md + tests/fuzz/CLAUDE.md to the spec author, then
src/core/internal.h + src/core/CLAUDE.md). The pattern is now stable
enough to treat as a standing property of spawning: every D27-style brief
must anticipate it and require disclosure, and blindness constraints must
be written knowing ambient CLAUDE.mds WILL leak. (2) The main session
began reviewing the delivery while the author was still mid-flight (the
watch fired on the first file change) and briefly misread in-progress
work as incomplete — the worktree convention Frank ruled this session
exists to make that impossible; this addendum is its second motivating
incident.

## 2026-08-11 — eighth session: stale-watcher cleanup; slice 8 (the ASK contract + the cursor-rule channel)

**Housekeeping first, on Frank's report:** 17 stale watcher shells from
previous sessions were polling forever — each `until ! pgrep -f "...";
do sleep N; done` matched the OTHER watchers' command lines, a mutual
deadlock by pattern. Stopped via the harness (TaskStop by task id, mapped
from /proc/PID/fd/1 → task output file; a direct `kill` was blocked by the
permission classifier). Lesson for hand-off watches, adding to the
seventh session's: a pgrep-based quiet-check must anchor or exclude its
own observers (`pgrep -f` sees every watcher quoting the same string), or
better, key on a done-marker file. The ~88 idle AGENTS in the panel are
inert conversation state, not processes — nothing to clean.

**Slice 8 = the ASK contract (§18.2 as ruled) + the probe channel**
(this commit). ExtWant {CLAIM, VERDICT, RESULT}, no `may` axis, threaded
through all four doorway signatures; parse.c's six call sites ask
WANT_RESULT (the real parse wants the construct); `ext_gate` demotes
RESULT→VERDICT — the §5.4 gate with an empty enabled set, unconditional
today, floors at VERDICT never CLAIM; ExtResult gains `answered_at` (the
post-gate level; nothing on the compile path reads it, byte-identity
asserts that). The channel: `pcrec --probe-ask WANT [--] TEXT`
(pcrec_probe_ask, syntax_dump.c) drives ONE doorway call placed exactly
as parse.c places it and reports the REAL cursor before/after — the
harness computes both sides from observed runs, per the check-design
lesson (never echo a field the implementation also wrote).

**Two routing findings, measured on the first sweep.** (1) Ten rows'
syntax carries a plain-group prefix (`(a)(?-1)` — the probe must compile
in PCRE2), so prefix routing missed them: the channel now scans bytewise
to the first doorway OPENER and reports full-text coordinates, exactly
where parse.c would have the cursor. (2) `(?:` driven at the group
doorway hits BAD_ROW ("malformed registry row") — because parse.c
answers `(?:` BEFORE the doorway and the RS_BASE row is never looked up.
The channel now excludes `(?:` exactly as parse.c does; probing a call
that cannot happen is not a measurement. 99/100 rows route (the `(?:...)`
row is the deliberate exception), × 3 want levels, cursor unchanged
everywhere; `result` asks visibly answered at `verdict` — the gate
demotion is now a measured fact, false the day the first module lands.

**Verified:** 952-pattern byte-identity differential vs the pre-slice
binary (slice 5's instrument, reused): zero differences. cli case10
95→109: exact cell, 10-field count, gate pin, cursor sweep FLOORED at
198 probes, exit-code split (measured refusal exit 0 ≠ channel-cannot-run
exit 1). Three sabotages, each caught by its intended instrument with
the counts predicted beforehand: cursor breach under !RESULT → 82/82
sweep probes + the exact cell; ext_gate returning want unchanged → the
gate pin alone (1 failure); REFUSE dropping answered_at → 2 failures.
Full battery green (suite, strict, verify_rxt, fuzz seed 1, spec_mod0
7/0/3, mech).

**Parallel tracks this session:** DOC-1 cold reader spawned (read-only,
denied src/tests/plan/journal/design; re-derives the seven lost
spec-ambiguity findings). Next spawn: the FRESH D27 author for check06's
comparison — in a worktree under worktrees/ per Frank's ruling.

**Next:** check06 arming (D27, worktree), then the enabled-set/toggles
surface (checks 01/07/09), then MOD-0.1's byte-identity landing bar.

## 2026-08-11 — eighth session, second stretch: DOC-1 closed (eleven findings reconciled)

DOC-1 ran as the parallel track while slice 8 verified: a fresh cold reader
(read-only, denied src/, tests/, plan, journal, design doc) re-derived the
lost spec-ambiguity findings from the six goal documents alone. ELEVEN
findings, quotes and line numbers for each; all eleven reconciled in one
commit, dispositions in plan.md's DOC-1 entry. The sharpest was the D26
tier-2 shape this project keeps finding in its own documents: the hand
half of pcre2_compliance.md assigned `\N{U+hh..}` to module `classes`
while the generated index in the SAME file said `unicode-props`, and the
cross-reference that would have resolved it pointed at a note that had
never been written. The registry wins (it is measured); the note now
exists and covers the three-way `\N` clash. Also: `^`'s unexplained
OK-LIMITED resolved by probing (correctness gap = multiline, same as `$`;
the D8 engine caveat is SPEED and now says so), the OK-LIMITED and
`becomes` vocabularies tightened (limit KIND per row; `never` defined;
revisit-trigger ≠ plan), README's optimizer-as-roadmap and first-commit
corpus count fixed (counts read from runs now), pcrec.h scopes the
caseless zero-cost claim (D23) and the streaming absence (M3.0's gate),
APPROACH's "req. N" citations flagged as founding-brief numbers with no
in-repo referent — Frank could check the brief in — and D18/D26 gained
their supersession/pinning markers. Registry+compliance checks green
after the edits (143/143).

Process: the reader disclosed the FOURTH D27 ambient-injection instance —
docs/CLAUDE.md and lib/CLAUDE.md auto-injected on first Read into those
directories, including K10's description, which overlaps its top finding;
disclosed, and the finding cites only the two contradicting tables. The
leak pattern remains a standing property of spawning; the disclosure
requirement in briefs is doing its job.

## 2026-08-11 — eighth session, third stretch: slice 9 (the enabled set, the scans TU, the real gate)

**Slice 9 = the enabled-set/toggles surface** (this commit), scoped by the
spec checks' own discovery conventions rather than by taste: check01 finds
the enabled-set symbol AND the recogniser/extent-scan TUs by nm-name
convention and fails-as-missing if either discovery is empty, so the slice
owed three things at once. (1) enabled.c: the set's one home —
process-wide, written once by `--features LIST` before any compile
(module names as the dump spells them, all/none, unknown names refused BY
NAME per the --flavour rule; NOT a pcrec_options field, D20 keeps the
core option surface scalar). (2) scans.c: the always-live extent scans
extracted from ext.c — the K4 three-rule delimiter-pair scan with its
rule documentation and four pin patterns, pair_opens as its predicate,
the verb-name extent — pure (pat,patlen) signatures, `*_extent_scan`
names, and a TU that never links the enabled symbols. nm confirms the
whole §12 story mechanically: ext.o (the seam) carries the one undefined
reference to pcrec_feature_enabled; scans.o carries none. (3) ext_gate
became the real membership test, AFTER row choice: NULL row and
RS_REJECTED rows always demote; an ENABLED row keeps WANT_RESULT, so a
refusal's answered_at now distinguishes "gate open, port missing" (the
D33 NULL-port refusal) from "gate closed" — measured: `--features all`
flips '\d' result-asks to answered_at=result, `--features backrefs`
does NOT (per-module, not blanket), and neither cursor nor verdict text
moves under an open gate.

check01 SELF-ARMED on the surface's arrival and PASSES (4 symbol/TU
pairs over 1 recogniser TU; its own sabotage — one reference from
scans.c — caught with object and symbol named). SPEC-MOD0 is 8/0/2.
Byte-identity: the 952-pattern differential against the PRE-SLICE-8
binary still shows zero differences — the default empty set is inert
through both slices. cli case10 109→117.

**The basename lesson, paid a third time:** the new byte-identical-under-
--features-all case first compared feat_a.c against feat_b.c and failed —
the emitted C embeds the output basename in its #include. Same basename,
two directories. The lesson is now load-bearing in a committed test
rather than only in the journal.

**Next:** merge the check06 author's worktree delivery when it lands
(then run the one-line src sabotage against the armed check myself);
spawn the check07-comparison author (surface exists now); then the
byte-identity landing bar closes MOD-0.1.

## 2026-08-11 — eighth session, fourth stretch: check06 merged and src-sabotaged; SPEC-MOD0 at 9/0/1

**The check06 delivery merged** (5b81c45, worktree branch check06-arm —
Frank's worktree convention, first full use: atomic delivery, reviewed as
a diff, merged with --no-ff). Reviewed and independently re-verified
before merge: the armed comparison drives all three want levels per row,
asserts clear-side equality separately at claim AND verdict (two code
paths), set-side >=, compares the non-routing set for EXACT equality
against {(?:...)}, floors five populations (unpinned-is-a-failure
implemented in the check itself), and detects the surface via --help
rather than assuming. The author's three-direction validation held up;
its predictor (all equalities today, >= branch live-but-unexercised)
matched its run with no correction.

**The invariant's own sabotage, run by the main session post-merge:**
one line in the escape doorway (cx->pos++ under want != WANT_RESULT) →
check06 FAILS with 82 disagreements (41 escape rows × claim+verdict),
each naming the row and printing the before/after pair; suite 8/1/1.
Restored pristine → 9/0/1. Both instruments now cover the rule: cli
case10's in-repo sweep (fails the same sabotage 82/82 in make test) and
spec-side check06 (independent authorship, runs at checkpoints).

**SPEC-MOD0: 9 pass / 0 fail / 1 awaiting** — only check07's comparison
remains, and its surface (--features) exists as of slice 9. Bookkeeping:
CLAUDE.md summary + table rows 1/7 updated for the landed surfaces.

**Process, the FIFTH D27 ambient-injection instance, with a new wrinkle:**
the check06 author's context received the WORKTREE's own CLAUDE.md copies
mid-task — including worktrees/check06-arm/tests/CLAUDE.md, a denied
path — triggered by editing files under those directories. Worktrees
make DELIVERY atomic; they do not contain the leak, they relocate it
(the injected copies are the worktree's, byte-identical to the main
tree's). Disclosure worked; nothing consumed; the standing rule stands.

**Next:** spawn the check07-comparison author (fresh D27, worktree, on
this HEAD); then the byte-identity landing bar closes MOD-0.1.

## 2026-08-11 — eighth session, fifth stretch: the byte-identity landing bar MEASURED — PASSES

The bar (plan: MOD-0.1's close condition) ran against the true pre-MOD-0.1
baseline: daf3518 (post-FIX-3, pre-slice-1), rebuilt in a detached
worktree and compared over 1,045 patterns — every registry syntax probe,
every corpus pattern, every simply-quoted reject/accept pin, the four
doorway byte sweeps and the delimiter shapes — on (exit, stdout, stderr,
out.c, out.h). RESULT: 1,029 byte-identical; 16 differences, every one
guarded; 0 unguarded. The guarded set decomposes exactly as the plan
predicted: 6 K14 diffs (module promises → the no-promise ROADMAP_NEVER
diagnostic), 10 K12 diffs (endpoint cells → "invalid range in character
class", plus the two EVALUATION-ORDER cells — [\d-\A] and [\d-\p{Foo}],
where which of two real refusals surfaces moved; both pinned with
rationale at tests/reject/run_reject_tests.sh:230-231, and the bar
enumerates them BY PATTERN so a third instance fails until pinned). No
exception touches an emitted out.c: accepted patterns are byte-identical
across the whole of MOD-0.1. The instrument's detection is live, not
assumed — its first run reported those two order cells as UNGUARDED
before the enumerated guard existed.

MOD-0.1's close condition is therefore: bar PASSED, full suite green
(slice-9 battery), SPEC-MOD0 at 9/0/1 — closure waits only for check07's
comparison (author in flight in worktrees/check07-arm; its surface is
slice 9's --features and is no longer missing).

## 2026-08-11 — eighth session, sixth stretch: the D27 CELL (Frank's ruling on the injection leak)

Frank ruled the fix for the ambient-injection leak: keep the worktree as
the DELIVERY target, and give the author a parallel, NON-GIT, allowlist-
filtered CELL to work in. Done manually first, then scripted once it
worked (scripts/mk_d27_cell.sh, with its own CLAUDE.md; convention
recorded in the root CLAUDE.md beside the worktree ruling it amends).

What the manual walkthrough established: the cell (tests/spec_mod0 +
tests/probes + tests/fuzz/pcre2_abi.h + a build/ prebuilt INSIDE the
worktree so the binary matches the delivery branch) runs the full
spec_mod0 suite identically to the main tree (9/0/1) with no source
tree and no .git; an author edit rsyncs back into the worktree and
appears as an ordinary reviewable git diff. Hygiene is verified by the
script itself (no git metadata, every top-level entry explained by the
allowlist), the allowlist is validated BEFORE anything is created (a
typo leaves no debris — the first version left a worktree behind, found
by testing the failure direction), and the script prints the exact
diff-back/review/teardown commands.

Why cell beats worktree-alone, recorded for the next reader: the
injection needs the file to EXIST in a directory the agent touches —
allowlist copying removes the denied files' existence, not just
permission; and a git worktree hands the author full history (git show
HEAD:src/... defeats instruction-level blindness), which non-git
removes. Allowlist, never denylist: a denylist miss leaks SILENTLY, an
allowlist miss fails LOUDLY. The residual spawn-time injections
(session-root CLAUDE.md, memory index — present in instances 4 and 5)
are unavoidable without leaving the project directory; briefs keep the
disclosure requirement for exactly that residue.

The check07 author, already mid-flight under the old convention when
this landed, finishes under it (its brief carries the disclosure
requirement); the next D27 spawn uses the cell.

## 2026-08-11 — eighth session, close: check07 merged; MOD-0.1 COMPLETED

**check07 merged** (50966bf). The author's two judgment calls were both
right and both survived review: (1) the compared-pair definition was
corrected BEFORE landing — accepted-under-all-on eligibility, because the
naive count would have claimed 1,700 meaningful pairs while nothing has
ever been let through a gate (C4/F4's exact vacuous-pass shape; the 1,700
verdict-class checks still RUN over the whole registry, 0 disagreements,
they just don't count as compared pairs); (2) AWAITING-POPULATION rather
than PASS — the surface exists and the comparison runs, but a check that
cannot yet disagree must not report a pass. The load-bearing addition:
a separate instrument-LIVENESS check (via --probe-ask's answered_at),
because a no-op --features would pass the class sweep exactly as well as
a live one — the author independently identified the
control-sharing-a-source shape and routed around it. My own src-side
sabotage post-merge confirmed it: gate wired to ignore the enabled set →
check07 FAILS at the liveness check naming the exact probe, 1
disagreement; restored, suite 9/0/1. SIXTH D27 leak instance disclosed
(worktree CLAUDE.mds; author predates the cell convention — the next
spawn uses scripts/mk_d27_cell.sh).

**MOD-0.1 CLOSED against its landing bar** (plan.md STATE flipped, the
three conditions and their numbers recorded there): byte-identity
1045/1029/16-guarded/0-unguarded vs daf3518; SPEC-MOD0 9/0/1 with the
one awaiting being a POPULATION owed by MOD-0.3+, not a surface;
full battery green. Started sixth session, closed eighth: nine slices,
four K-issues (K11/K12/K13/K14), five checks armed by four blinded
authors plus one self-arming, one refuted-and-corrected design (D33 →
Part II → §18), and a byte-identity guarantee that the whole mechanism
change moved nothing it did not pin first.

**Next session: MOD-0.2** (migrate the 18 tail-bearing rows — read it
THROUGH the §18-resolved design; the reachability differential gates the
`-\d+)` collapse), with MOD-0.3 (classes) behind it as the first module
with ports — the moment check07's population goes nonzero, check02's
compared floor ratchets, and the K12 certification scope grows.

## 2026-08-11 — ninth session: MOD-0.2 COMPLETE — the tail engine retired for recogniser + rank

**Frank's directive:** MOD-0.2 and only MOD-0.2. Baseline verified first
(full battery green at fc981e3, mech 20/20, spec_mod0 at its designed
9/0/1), the pre-change binary snapshotted to the scratchpad, and the
differential instrument rebuilt from the journaled MOD-0.1 method before a
line of src changed: 4,330 unique patterns (registry probes, corpus,
simply-quoted reject/accept pins, verb forms, four doorway byte sweeps,
tail sweeps at all four migrated buckets, delimiter shapes) x three
channels (compile on (exit, stdout, stderr, out.c, out.h) with the same
basename in two directories; --count-groups; --probe-ask x three wants x
{default, --features all}) = 5,247 comparisons per run. Identical-binary
control: zero. Instrument liveness proven before any real result was
trusted: an inverted-rank sabotage build produced 910 differences.

**The interface, read through the resolved design (D32 §§2-4,7,9; Part II
§14.4):** RegRow gains `rank` and `recognise` as trailing fields; a NULL
recogniser means `pcrec_recognise_tail_default` with the row's `tail` as
parameter — after this step the field's ONLY reader on the lookup path.
Rank tiers 0 (fallback / never clashes), 25 (tailed), 70 (`\N{U+`). The
D30-era 40 tier is deliberately not reproduced: rank values are
meaningless except between clashing rows (D32 §3), and `\N{` clashes only
with the fallback below it and `\N{U+` above it. `pcrec_registry_arbitrate`
runs every sel-matching recogniser (sel kept as the checkable pre-test,
D32 §7); highest answering rank wins; a tie AT THE WINNING RANK is the
defect, surfaced by the escape/group doorways as an internal error — a tie
below the winner is rank doing its job and is deliberately not one.

**Four slices, committed separately, full battery + differential between
each** (1cc6ed6, 0aec468, bade9dd, c1e203d):

1. Data + unwired engine + checks. check_row_ranks (successor of
   tailed-beats-fallback; 18 tailed rows, the measured count), and
   check_arbitration_liveness — the R11/M3 more-than-one-answer counter,
   check_tail_precedence's liveness clause re-homed. Floors PREDICTED from
   the generator before the first run (10/15/15/50 multi-answer probes per
   bucket, 5 triple-answer at esc-'N') and confirmed exactly. The D32 §9.5
   migration scaffold compared the unwired arbitration against the live
   tail engine: 261,193 probes, 0 mismatches, 0 ambiguous.
2. Wiring. find() delegates to arbitrate; doorways own the ambiguity
   refusal. Differential ZERO over 5,247 — the seam moved engines with
   nothing observable moving.
3. Retirement, one commit for both: the reference engine AND its scaffold
   (an equivalence check cannot outlive its oracle honestly — D32 §9.5's
   rule, followed to the letter). Stale SR-9 prose rewritten at both homes
   (RegRow.tail's doc, the \N shortest-first comment). Counts re-read from
   runs: registry 166 then 165 after slice 4, reject 430, PC-3 143.
4. check_tail_precedence retired in its OWN edit, successors committed and
   green FIRST — the plan's sequencing rule held exactly.

**The ambiguity path validated live, not asserted:** an equal-rank
sabotage on the \N pair (70 -> 25) makes `\N{U+0041}` answer "internal
error: ambiguous registry arbitration for an escape", clean exit 1, and
fails 2 registry checks naming the row. Restored; pristine reruns green.

**The `-\d+)` collapse did NOT land**, per the standing rule: ten digit
rows stay ten rows. It waits for a reachability differential that passes
on `(a)(?-1` / `(a)(?-1x)` / `(a)(?-1:x)` (PCRE2 114) — unchanged.

**Landing bar:** differential vs the pre-MOD-0.2 snapshot ZERO differences
over 5,247 comparisons — a pure seam migration with NO guarded exceptions,
which is what the step promised. Full battery green (make test with 165
registry + 430 reject + PC-3 143, strict, verify_rxt 100%, fuzz seed 1
zero divergences, spec_mod0 9/0/1, bench, mech 20/20).

**Lessons:**
- `-Wextra`'s missing-field-initializers turns "append zero-defaulted
  trailing fields to a positional-literal table" into a per-row obligation
  — `make strict` failed on the first build, and the fix (every macro
  initialises both fields explicitly) is now itself the enforcement: a
  future row cannot omit rank/recognise silently. The zero-default design
  survived; the SILENT half of it did not, and that is an improvement.
- The wake brief predicted mech anchor drift (S15-S19) from registry.c
  edits. It did not happen, and the reason is the edit SHAPE: macro
  DEFINITIONS changed, call sites did not, and the anchors quote call
  sites. Worth remembering as the drift-avoiding way to widen a row schema.
- Predict-then-measure kept paying: the liveness floors were derived by
  hand from the generator before the first run and matched exactly, which
  is the difference between floors and numbers copied from output.

**Next:** MOD-0.3 (classes) is the head of the spine — first module with
real ports, check07's population comes due, PC-4 lands with it. NOT
started without Frank, per the session directive.

## 2026-08-11 — ninth session, close: the R15 panel and its fixes

Three narrow-brief read-only critics on the landed migration (checks lens,
engine lens, docs lens — one primary question each, the R12 standard; all
disclosed their ambient injections). Compiled with dispositions in
docs/reviews/2026-08-11-r15-mod02.md. The engine critic found NO
behavioural divergence. Four findings fixed the same session, each cheap
because the probe spaces already existed:

- **The no-ambiguity sweep** (engine critic): deleting the D32 §9.5
  scaffold had left the `ambiguous` out-param probed by NOTHING — a future
  same-rank prefix pair would fire only in a user's compile.
  check_arbitration_liveness now sweeps every kind × sel × generated text
  (261,193 probes, 0 ties); the equal-rank sabotage fails it directly,
  naming the probes.
- **registry_check's own count + manifest guard** (checks critic): the
  directory that DOCUMENTS why deletions must fail had the protection on
  PC-3 only. Mirrored for registry_check (count 166, three needles, plus
  one NEGATIVE needle — the retired check's PASS line must not reappear).
  Validated: deleting check_row_ranks fires both layers.
- **Tails only at esc/group** (checks critic): scans.c's prose assumption
  is now check_row_ranks' assertion — the other two doorways ask the
  tail-less question and discard ambiguity, so a tailed row there would be
  unreachable with silent clashes.
- **K10's stale nets list** (docs critic): named the deleted
  check_tail_precedence in present tense; now marks the retirement AND
  states the successors miss K10 the same way — the blind-net count did
  not shrink, which is the honest sentence the old text only implied.
- The duplicated dispatch predicate is gone: registry_check counts answers
  with the engine's own exported pcrec_registry_row_answers.

**The finding that was REFUTED, recorded because the refutation method
matters:** the checks critic proved the two new checks blind to
winner-swaps (true — they are, by design) and concluded a rank-value swap
(`\N{U+` at 24 vs `\N{` at 25) ships through `make test` green. Measured:
it fails check_table_to_parser TWICE inside make test — the per-row syntax
check is D32 §9.1's primary instrument and was in place before MOD-0.2
began. One sabotage build settled what the report argued. Verify a
critic's consequence claim the way you verify your own: run it.

Final state: registry 166 + reject 430 + PC-3 143 all from runs, strict
clean, differential vs the pre-MOD-0.2 snapshot still ZERO over 5,247,
spec_mod0 9/0/1, mech 20/20, bench clean. MOD-0.2 closed.

## 2026-08-12 — tenth session: MOD-0.3 (module `classes`) opened — baseline + the design gate

Frank's directive: begin dev. MOD-0.3 is the head of the spine and §18's five
decisions were all resolved in the fifth session, so nothing gates it.

**Baseline re-verified before any edit** (wake §3, exit statuses captured
directly, `FAIL:` grepped unanchored across every log: zero): make, make test,
strict, verify_rxt 100%, fuzz seed 1 zero divergences, spec_mod0 9/0/1 exit 1
(the designed awaiting state — check07 AWAITING-POPULATION), bench 0 budget
failures. mech pending at the time of this entry; recorded below when done.

**[MOD-0.3] expanded in docs/plan.md and STATE:started.** Substeps .3a-.3f,
each read THROUGH the resolved design (Part II §§12-16 as R14-corrected, D33
as amended, §18). Two conflicts in the old step text corrected on expansion,
struck in place: `pcrec_ext_class_pair_opens` is NOT collapsed (R14 (c) —
three critics independently; it IMPLEMENTS the deviating cell), and
`RF_CLASS_INVALID` does not stay as data (D33 §3/D34-7 retire it with
RF_CLASS_BASE; NULL class port = permanently invalid, the mode-invariant
half of §14.3 R14 verified).

**Scope measured before scoping** (probe_mod03.c, scratchpad, predictor
stated first; against libpcre2 10.46):

- `[[:^alpha:]]` COMPILES, census == `[^[:alpha:]]` exactly (204 members,
  0/256 diff) — negated names join the named-class port's scope.
- `[[:^foo:]]` / `[[:^<:]]` both err 130; pcrec's shipped answers at both
  are already right (module promise / unknown-name), no pre-existing defect.
- `[[:<:]]` / `[[:>:]]` COMPILE as zero-width word-boundary assertions
  (`[[:<:]]ab` → [0,2) on "ab"; `a[[:<:]]b` → no match on "ab").
- `(?[[a]])` COMPILES — extended classes are REAL 10.46 syntax; `(?[a])` is
  its own err 216, "unexpected character in (?[...]) extended character
  class".

**MOD-0.3a rulings (the design gate; D6 panel stays at close):**

1. **No enabled-module-still-refuses lie.** With `classes` on, everything
   still refused must answer an honest name. The POSIX name list gains
   per-name structure (the K14/VerbName precedent): 14 character-class
   names stay `classes` and become producible; `<` and `>` move to module
   `assertions` — the module `\b`'s own row already carries, and the
   registry's comment at posix_names[] assigned this split to whoever
   implements the doorway. `(?[` re-attributes from `classes` to a NEW
   module `extended-classes` (real syntax, RD_PLANNED, no milestone owner
   yet — the name discharges the obligation under D26). Consequences,
   accepted: 17 module names; check09's coverage count and the reject pins
   move BY MEASUREMENT; `--features all` picks the new name up
   automatically; feature mask 17 < 32 (D34-3's loud ceiling far off).
2. **Ports are two trailing tagged fields on RegRow** (atom port, class
   port), kind ∈ {NONE, SCALAR, SET, FN}: NONE at atom = refuse as today,
   NONE at class = permanently invalid (NULL's one meaning, §14.3); SCALAR
   and SET are data (`\b` → 0x08; the char-types' 32-byte bitmaps); FN is
   the bounded row-local scan (octal, posix-name — §18.2's VERDICT
   legality). Every macro initialises both fields explicitly: -Wextra's
   missing-field-initializers IS the enforcement (MOD-0.2's measured
   lesson), and the edits stay in macro DEFINITIONS so mech's call-site
   anchors hold.
3. **The set bitmaps are generated FROM libpcre2 censuses** (a probe emits
   the C tables), never hand-typed, and PC-4 re-measures them against the
   live oracle every run — the PC-3 pattern; a version bump is a deliberate
   re-measurement event (D26 addendum). python re independently oracles the
   \d \D \s \S \w \W corpus blocks.
4. **The corpus channel is a per-block `features <list>` directive** in
   .rxt beside `flags` (run.sh forwards `--features <list>`); \h \H \v \V
   \N and POSIX blocks are `# pcre2-only` by construction, the rest keep
   the python oracle.
5. **Slice order keeps byte-identity until the wiring slice**:
   esc_class_value stays parse.c's class-side octal/literal engine through
   slices 1-2 and becomes the FN-port callee in slice 3 (its bare int →
   tagged claim, the K11 shape named in D33 §8). Class structure stays
   8-bit (D33 §7; MOD-0.6 owns widening).

FLAGGED TO FRANK (tier-2 attribution judgements, reversible data + pins):
the `<`/`>` → `assertions` move and the new `extended-classes` module name
are my rulings under D26's tier discipline, recorded here rather than
asked, per the begin-dev directive. Say the word and either becomes a
one-row edit plus pin updates.

**Mid-session (Frank): test parallelism.** `PROCS=N` landed in the two serial
loops worth parallelizing, opt-in, default 1 = byte-identical behaviour:

- `tests/harness/run.sh` — per-FILE workers (self-reinvocations, own temp
  dirs, output replayed in file order). The parent judges a worker ONLY by
  its printed summary; a vanished worker is a hard failure. Validated in the
  failing direction twice: a planted wrong expectation propagates (exit 1,
  detail line intact) and a deleted worker output fires the guard ("1 of 2
  file workers reported", HARD FAILURE). Measured: full corpus 1139/0/0 over
  25 files, 4m25s serial → 55s at PROCS=6, counts identical.
- `tests/mech/run_sabotage_matrix.sh` — concurrent sabotages (run_one was
  already isolated per sabotage), rows merged in sabotages/ listing order,
  JOBS defaults to nproc/PROCS. Measured: 6m20s serial → 1m57s at PROCS=4,
  detection tables BYTE-IDENTICAL unsorted, 20/20 DETECTED both ways.
  **The change also closed a pre-existing hole**: the summary's denominator
  was `wc -l` over the rows that ARRIVED — the same source as the numerators
  — so a sabotage whose definition failed validation produced no row and
  19/19 read as clean. The guard now counts the demand side from the
  `sabotages/S*.sh` listing in BOTH modes; validated with a stub missing
  SAB_FILE (FATAL exit 2, the missing sabotage named). The
  checks-sharing-a-source catalogue gains its counter-example.
- `make bench` stays deliberately parallel-free in both directions (D12/D17
  timing medians, loadavg gate) — documented in docs/testing.md.

**Slice 1 (MOD-0.3b) — vocabulary + port columns, unwired.** ExtWhat gains
EXT_SCALAR / EXT_MEMBERS / EXT_NODE (unconstructable until the producers
wire; pcrec_ext_finish walls a premature arrival as an internal error);
ExtResult gains the production payloads; RegRow gains `aport`/`cport` —
tagged {NONE, SCALAR, SET, FN} ports, every macro initialising both
(-Wextra enforcement, the MOD-0.2 property, held: make strict green on
first try after 14 macro edits). The doorway vocabulary block moved above
RegRow in internal.h — ports embed it, the dependency inverted. Data
landed: \b -> 0x08, \g \k \8 \9 -> their letters (ESC_CLASS_BASE gained a
scalar parameter — its three callers are exactly the fixed-byte rows;
ESC_DIGIT_LIT split for \8/\9, which have no octal continuation). \0..\7
stay portless until the octal FN wires (slice 3).

check_class_ports: populations predicted BEFORE the first run (5 scalar /
0 SET / 0 FN / 0 atom) and confirmed; values oracle-tied — a bare-escape
row's scalar must equal its libpcre2-fed class_expect byte, so the port is
never its own authority; body-carrying rows (\k<name>, \g{-1}) tie to the
selector letter per §14.3's fallback law. Sabotage-validated three ways:
0x08->0x09 drift fails the column tie, a zeroed \k scalar fails the
fallback law, deleting the call fires run_registry_tests.sh's count
(166->167) AND the new manifest needle.

Byte-identity: 243 corpus patterns x (verdict, diagnostic, emitted C)
against the post-attribution snapshot binary — ZERO differences; the
instrument proven live first against the pre-MOD-0.3 snapshot (the
attribution diagnostics differ, and it sees them). Sabotage-anchor check:
S15-S19 quote call-site lines this slice did not touch (macro DEFINITIONS
and the five scalar call sites only; the drift-avoiding edit shape, reused
deliberately). mech re-run against the slice-1 commit follows it.

**Slice 2 (MOD-0.3c) — THE PRODUCERS. pcrec compiles its first non-base
constructs.** Under `--features classes`: the ten char-type escapes at both
positions, bare `\N` at atom position, and the POSIX named classes with
both polarities (`[[:^alpha:]]` measured real in .3a) — matched end-to-end
(`\d+` finds [3,6) in "abc123def" through the emitted C). Default state
byte-identical (243-pattern differential vs the slice-1 HEAD build, zero
differences).

The shape: bitmaps GENERATED from libpcre2 censuses (probe_cls_bits.c —
predictor stated first, confirmed exactly on all 20 tables; the complement
law asserted before emitting, so negation is a port FLAG and only positive
tables exist to drift); ports on rows (SET data for char-types and \N,
PORT_FN for the posix name row — one row, fourteen names, two polarities);
`pcrec_ast_class_from_bits` the ONE set-node constructor, owning
fold-before-negate (the caseless×posix cells measured before pinning:
probe_ci_posix.c, 8/8). Wiring: the escape doorway answers post-gate
WANT_RESULT from the position's port (EXT_NODE atom / EXT_MEMBERS class);
esc_atom splices, p_class ORs and moves the cursor to res.end (the caller
moves, never the doorway — check06 held without edits). The endpoint rule's
step 4 now keys on ANY surviving claim, so [0-\d] is invalid-range in both
gate states — §16.3's composition bullet, live.

**check07 found its first real disagreement set, and the finding ran the
other way.** The moment the population arrived (12 eligible rows), the
sweep reported 24 disagreements — every one the gate DOING ITS JOB
(accepted all-on → refused-as-unimplemented with classes off). The check's
own CLAIM paragraph ("a disabled feature changes what pcrec can COMPILE —
that is the point of a gate") had stated the right invariant all along; the
implemented strict equality was the exercisable subset while nothing could
flip. Replaced with the TRANSITION RULE (dated correction in the header):
an eligible row MUST flip to refused-as-unimplemented NAMING ITS OWN
module — still-accepted is a DEAD GATE, the direction equality was
structurally blind to, and the new clause was sabotage-verified (an
ext_gate that never demotes fails 24 clauses by name); everything else
keeps equality, so cross-module leaks still fail. Floors: eligible 12,
baseline_accepted 13; compared_pairs stays floor-0 deliberately (check09's
per-name assertion arms on it and would demand all 17 modules toggle —
MOD-0.8 work; the pair count is transitively ratcheted through
pairs==eligible×2). **tests/spec_mod0 exits 0 for the first time in
project history: 10 pass, 0 fail, 0 awaiting.**

Corpus: tests/classes/classes.rxt (first per-module test directory), 43
cases green, python oracle 20/20 on the expressible blocks — and the D33
§9.3 record measured for real: against the slice-1 binary the corpus fails
37 with 31 distinct compile failures. The `features` directive landed with
a VALIDATED spec (pcrec refuses unknown module names with exit 1, which a
perr block would have read as success — the typo path is a loud harness
failure instead). S15/S16/S17 anchors re-derived for the ESC_SET call
sites in the same change, per the anchor convention.

**Slice 3 (MOD-0.3d) — the retirements, with the design meeting reality
three times.** RF_CLASS_BASE retired into BASE ports: ExtPort gained a
`base` bit (§14.3's per-port gating — [\b] is backspace and [\12] octal
WHATEVER is enabled), \b/\8/\9/\g/\k are scalar port data, \0..\7 the
octal PORT_FN (pcrec_clsport_octal stays in parse.c: base grammar's own
rule migrated to the seam, message and offset byte-identical — err 151 at
the ran-out position). parse.c's FIX-3 block and \b special case are
DELETED; the doorway is entered at class position for all thirteen rows
and the port answers at the level the caller ASKED, gate untouched.
registry_check re-keyed both RF_CLASS_BASE readers onto the port; the
in-class sweep gained excuse_base_cport (scoped to that sweep only, so an
atom-position mismatch on those rows cannot hide behind it);
check_class_ports 5/10/9/11 predicted then confirmed. Byte-identity in
BOTH gate states: 243 × (verdict, diagnostic, emitted C) vs the slice-2
build, zero differences; the 127 FIX-3 pins and the classes corpus green
through the migrated path.

**The deviations, because the measured world disagreed with the plan text
three times:** (1) RF_CLASS_INVALID stays — D33 §3's "NULL regains its one
meaning" is false today: the lexical rows' class_expect is "err 106" for
PROBE-SHAPE reasons ([\Q] quotes the closing bracket — K13's
column-measures-the-probe lesson, re-met), and unicode-props' rows carry
honest NULLs that are "awaiting MOD-0.6", not "permanently invalid".
Deriving invalidity from the measured column would have rewritten [\Q]'s
answer wrongly. Retirement goes to MOD-0.6, when the port population is
total. (2) RF_CLASS_DELIM stays as DATA — conversion to a recogniser buys
nothing observable and churns the R9-hardened doorway dispatch; the flag
is the construct's recognition rule as data, which is D29's line, and
pair_opens already survived R14 as code where code is needed. (3) The
in-class tail-sweep extension defers WITH RF_CLASS_INVALID (D33 §9.2
conditioned the obligation on the removal; K10's blind-net count is
unchanged and stays MOD-0.6's).

**Backrefs design note recorded (Frank's question, tenth session):** the
digit rows' VM_ONLY is provisional — a backreference to a FINITE-language
group is regular and an AOT compiler can expand it statically ((a|b)\1 =
aa|bb, pure DFA, zero runtime cost, bounded by the existing caps); only
infinite-language groups need the VM's string-compare-and-backtrack. The
module's engine answer is per-pattern, not per-row. Home: the backrefs
paragraph in docs/plan.md, pointer beside the rows in registry.c.

**Atomic/possessive companion note recorded (Frank, same conversation):**
the (?> row's VM_ONLY splits like backrefs', with the intuition trap
recorded — a DFA never backtracks, so naive determinization gives the
NON-possessive semantics (a*+ab vs a*ab differ); the constructs are cut
operators (regular, Berglund et al.), and the cut construction's primitive
is the priority-first-accept function pcrec's subset construction already
computes. Homes: plan.md beside the backrefs note; pointer on the (?> row.

**Slice 4 (MOD-0.3e) — PC-4, the semantic differential, landed WITH the
module as its step always demanded.** 273 deterministic patterns (esc +
posix spellings × six shapes + a 39-pattern caseless block — the first
time -i has ever met an external oracle here) × 271 subjects shared
through ONE header both sides embed. Populations predicted exactly, then
confirmed on the first run: 232 both-accepted, 41 refusal agreements,
62,872 match cells, zero disagreements, ~2.5 s inside make test with
skip-loudly. Both failure axes proven live before the zero was trusted: a
one-bit bitmap sabotage names subject 0x35 per pattern; a dropped -i fold
names exactly the caseless posix cells.

**The sabotage that returned zero and was RIGHT to be distrusted:** the
first bitmap sabotage produced no failures because the Makefile's
hand-maintained header prerequisites did not include cls_bits.inc — the
edited table never entered the binary. Fixed in the same change (the .inc
joined the prerequisites, with the story in a comment). The R8 battery's
lesson one level down, met again: prove the sabotage reached the binary
before reading its zero. Without the liveness discipline, a regenerated
bitmap after a libpcre2 version bump would have silently shipped stale.

## 2026-08-12 — tenth session, close: R16 and the MOD-0.3 landing

**The landing bar, met before the panel:** default-config differential vs
the pre-MOD-0.3 snapshot (b6adda5 build) over 243 corpus patterns — ZERO
differences beyond the three pinned attribution diagnostics, shown
explicitly; PC-4 zero divergences over 62,872 cells; spec_mod0 10/0/0;
full battery green at every commit.

**R16 (three narrow-brief critics, all delivered; compiled with
dispositions in docs/reviews/2026-08-12-r16-mod03.md):**

- CHECKS: the corpus was blind to a lower/upper bitmap swap on a box
  without libpcre2 — MEASURED with the critic's exact sabotage (corpus
  43/43 green, PC-4 1,151 disagreements) — because every lower-adjacent
  block was caseless and the -i fold makes lower≡upper. Ten discriminating
  pins added, failing-direction validated. New catalogue sentence: a
  caseless pin is not a pin of the two sets it folds together.
- ENGINE: \N{2,3} refused where PCRE2 parses the brace as a QUANTIFIER
  and compiles bare \N repeated — a pre-existing row made into a live
  tier-2 divergence by this milestone's own producer. Boundary measured
  first (probe_nbrace.c, 22 cells; {,3} compiles — one of the critic's
  own cells corrected, and fuzz.py's a{,3} exclusion note found stale).
  Fixed with the table's FIRST custom recogniser + pcrec_brace_quant_shape
  — one pure scan, two load-bearing callers (try_quant's pre-test and the
  recogniser), so the two grammars cannot drift silently. esc-'N' liveness
  floor 10→9 with the exact probe text predicted; reject counts 265→268;
  corpus blocks landed; ^\N{2,3}$ matched end-to-end.
- DOCS: seven stale-as-current-fact findings, all fixed — the design doc's
  "Not built" banner, the compliance survey's REJECTED rows for shipped
  constructs (vocabulary gained OK-GATED), K13 naming the retired flag as
  live machinery, K10's stale citation, D33 §3's unmarked half-falsified
  prediction, and two src/parse/CLAUDE.md sentences from the pre-producer
  world. The reject-table maintenance rule updated for the gated era
  (default-state rows stay until a module goes default-on).
- Process: the engine critic self-reported and reverted a worktree write
  it caught itself making — the scope-mandate-in-every-brief discipline
  plus honest disclosure, working as designed.

MOD-0.3 CLOSES with this commit: the first module with producers, shipped
through five slices + a panel, every check moved with its surface, and
both panel findings fixed with machinery the design had already paid for.
MOD-0.5 (modifiers) is next on the D30 §7 spine — NOT started without
Frank, per the standing directive.

**Session-close discussion (Frank): the newline-convention axis, recorded
as DD-11.** pcrec is NEWLINE_LF and it is anchored by the oracle (every
measurement at options=0; \N's bitmap is the measured complement of
{0x0A}), not assumed; the (*CR)-family verbs refuse cleanly so the axis is
closed loudly. Cost prediction on arrival: ./\N fold like caseless;
$'s EOL assertion is the engine work (set-valued under ANY/ANYCRLF,
two-byte under CRLF, both DFAs). Details in the DD-11 plan entry.

**Session-close discussion 2 (Frank): the UTF architecture, recorded as
DD-12.** One parser; CharSet = code-point intervals as the parser's
semantic output; encoding = a per-instance LOWERING to byte-level NFA
(ASCII identity, UTF-8 interval expansion with suffix sharing); match time
stays byte-wise UTF-8 forever — code points exist only at regex-compile
time inside the CharSet, which is where the convert-to-UTF-32 instinct
belongs. Invalid-UTF semantics to be measured against
PCRE2_MATCH_INVALID_UTF. Details and owners in the DD-12 plan entry.

**R16 follow-up (Frank spotted the replication): the posix name->bits map
is generated, not hand-paired.** mod_classes.c's hand-written map[] was
the exact species of line the R16 lower/upper swap exploited; the pairing
now comes out of probe_cls_bits --emit as pcrec_cls_posix_map, part of the
same measured artifact as the tables, and mod_classes.c walks it. The name
LIST keeps its two legitimate other homes (different questions:
posix_names[] = existence + attribution, PC-3-measured; the probe's ents[]
= the generator), and registry_check now ties the map's name set to
posix_names[]'s producible names both directions — sabotage-validated
(deleting the graph entry from a scratch .inc fires both clauses).

**Session-close discussion 3 (Frank): subroutine calls by INSTANTIATION,
recorded as the third companion note beside backrefs/atomic in plan.md.**
The composition is the insight: PCRE2 subroutine calls are documented
implicitly atomic, so the AOT compile is inline-the-body PLUS the cut
operator from the atomic note — the two notes share the hazard (naive
determinization) and the cure (priority-first-accept). Engine boundary =
call-graph acyclicity at compile time; cycles ((?R)) are honestly
context-free and stay VM; (?(DEFINE)) is a macro library begging for
instantiation. Two measure-first obligations recorded: probe the
atomicity claim (documentation is a claim, not a fact here) and the
capture-restore wrinkle that returns when the VM grows captures.

## 2026-08-12 — eleventh session: MOD-0.5 (module `modifiers`) opened — baseline + the design gate

Frank's directive: begin dev; mid-session, manage parallel subagents with
appropriate models over non-interdependent sections, worktrees for writers,
the D27 cell generator for the blinded test author.

**Baseline re-verified before any edit** (wake §3 battery rebuilt in the
session scratchpad: make+strict serial; PROCS=6 make test | verify_rxt |
fuzz seed 1 | spec_mod0 concurrent, TMPDIR=/var/tmp; bench alone; PROCS=4
mech). Every exit 0 — spec_mod0 exit 0, its new normal; mech 20/20;
`FAIL:` grepped unanchored across all logs: zero. HEAD 1a38d3b, tree clean.

**[MOD-0.5] expanded in docs/plan.md and STATE:started; MOD-0.5a (design
gate) completed in the same commit.** Scope measured before scoping
(tests/probes/probe_mod05.c + probe_mod05b.c, predictions stated first,
libpcre2 10.46):

- The D30 §7 hazard cells confirmed exactly: `(?x)[a- ]` err 108,
  `(?xx)[a- ]` COMPILES with members {a,-}; escaped space stays significant
  at endpoints; xx deletes exactly {09,20} inside classes; single `x`
  NEVER touches a class interior.
- The x-mode skip set outside classes is {09,0A,0B,0C,0D,20,85} — 0x85
  (NEL) is skipped, so the set is NOT \s's (census 6). The first census
  template had quantifier false positives (`a*b` matches "ab" with no
  skipping); re-run with a no-x control column. Lesson re-learned in
  miniature: a census needs a control before its members are believed.
- SURPRISE, then non-finding: `a{1, 2}` and every spaced brace form
  COMPILE at options=0 as QUANTIFIERS (PCRE2 10.43+ rule). Checked pcrec's
  side immediately: pcrec_brace_quant_shape already accepts space/tab
  (R16's scan) and the emitted matcher agrees with libpcre2 on the
  discriminating subjects. No divergence; recorded in the probe header.
- `(?^)` resets i,m,n,s,x,xx and does NOT touch U or J (both probed
  surviving) — "unset imnsx", not "unset everything"; the reset is
  to-hardwired-constant (the PARSE-1 landmine, now load-bearing).
- `(?ri)` vs `(?i)`: 0 diff cells over 256 patterns x 256 subjects; all
  four `a`-sub pairs census-identical — r/aD/aP/aS/aT/aW are MEASURED
  no-ops at options=0 C locale, real again under UTF/UCP (MOD-0.6/M5
  pointer recorded).
- `(?n)` uncaptures plain parens (rc 2->1 on `(a)`), makes `\1` err 115,
  and does NOT imply J (err 143 preserved).

Rulings recorded in the plan entry (per-letter semantics vs honest
per-letter refusals — `m` -> 'assertions', `J` -> 'named-groups', tier-2
attributions FLAGGED TO FRANK; the measured (?^) rule; the measured x-mode
sets; malformed runs are the module's SYN_MALFORMED half with the gate ON).
Slices .5b-.5f staged with byte-identity first, the lexer third, checks
moving with surfaces, and the close panel + D27 cell writer last.

## 2026-08-12 — eleventh session: MOD-0.5b/c/d — the modifiers producers, three lanes in parallel

**The parallel fan-out (Frank's directive):** three sonnet subagents on
non-interdependent sections — impl-mod05b (worktree: the .5b grammar move),
corpus-mod05 (worktree: tests/modifiers/, oracle-verified, watched-failing
per §9.3), d27-mod05 (a BLINDED cell writer; allowlist narrowed to exclude
tests/probes so this milestone's measured alphabet could not leak into the
spec). All three delivered; the main session reviewed and merged each diff
serially with the battery between merges.

**MOD-0.5b (105aecf, merged 1c8883b):** the grammar move, byte-identity —
641 patterns + list surfaces + 69 probe-ask combos, zero diffs; moved code
diffed VERBATIM; the recogniser is a MARKER keyed by pointer identity (the
run starts AT the selector byte; `at - 1` in the shared recogniser would be
UB against registry_check's synthetic buffers). The worker went idle
uncommitted; the main session finished the landing bar and committed with
authorship noted.

**The D27 delivery (b337be2, merged 91e6b23):** check11 (113
recognition-boundary probes incl. the 40-letter alphabet COMPLEMENT with
runtime-computed exceptions) + check12 (39 behaviour cases; U-greed via
match spans; a 10-case scoping family armed on the across-| leak the writer
independently re-derived from libpcre2 — the same 17/17 semantics PARSE-1
measured, converging blind). Its refused_unimpl floors were DESIGNED
transition tripwires for this landing. Disclosure clean.

**MOD-0.5c/d (this commit) — the producers, ONE landing.** Sequencing
ruling: with the gate ON there is no honest refusal wording for `(?x...)`
before the lexer exists (naming 'modifiers' while enabled is the MOD-0.3a
lie; other wording breaks check12's classifier), so the slices landed
atomically. What landed:

- Ctx.caseless -> ModState {caseless, dotall, ungreedy, nocap, xlevel};
  THE SCOPE MECHANISM IS PLACEMENT: save/restore moved to p_group_body's
  body-parsing tail, so a bare run's doorway splice escapes its own paren
  pair's restore by construction.
- pcrec_modport_optrun: ONE handler for both spellings ((?run) mutates the
  enclosing scope + A_EMPTY; (?run:body) = set/pcrec_parse_body/restore);
  per-letter semantics i/s/U/n; ^ resets imnsx and PRESERVES U (measured);
  r/a-subs measured no-ops; m/J refuse per-letter to 'assertions' /
  'named-groups'; malformed runs diagnosed in the port (194/114 shapes).
- Three probe rounds beyond the gate's (all committed): unset-WINS in a
  run regardless of order; doubled-x is ADJACENCY-sensitive and a later
  bare (?x) DOWNGRADES xx; the x-lexer boundary (quantifiers/lazy markers
  bind across skips; comments end at 0x0A ONLY — the newline convention,
  not the skip set; the option run is lexically tight; newline-in-brace
  defeats quantifier-hood; xx deletion precedes negation, range parsing,
  and the dash lookahead).
- parse.c lexer: xskip / cls_skip / cls_peek_past_dash, every rule
  probe-cited. The D30 §7 hazard (?xx)[a- ] compiles to members {a,-}.
- reject_gated: a FOURTH pin class (own ratchet counter, 4 pins) because
  .rxt perr cannot assert WHY — the corpus author's finding.
- Floors moved with the surface: modsyn 105 compared / 8 refused, modsem
  35 / 3 — zero real disagreements across all 140 compared cells.
- Corpus merged: 59/59 green after ONE landing correction — the \t block
  had transcribed the RAW-TAB measurement onto the ESCAPE form; libpcre2
  measured the escape SURVIVING deletion (pcrec agreed before the fix).
  Both forms now pinned; xxmode header records the correction.
- Docs: compliance rows to OK-GATED (i/s/U/n/x/xx/^/r/a-subs; m and J
  carry their per-letter attributions); anchors moved in S08/S09 sabotage
  definitions, branch_count_check, run_parse_tests prose, case10's
  cursor-sweep premise.

Still open in MOD-0.5: [.5e] checks (mech rows for the lexer, fuzz.py's
stale a{,3} note at its next edit), [.5f] close (R17 panel; the D27
follow-up brief; docs sweep; wake).

## 2026-08-12 — eleventh session, close: R17 and the MOD-0.5 landing

**The panel (three read-only critics in parallel while the .5e battery
ran; compiled with dispositions in docs/reviews/2026-08-12-r17-mod05.md):**

- CHECKS: three correct-today-unguarded corners of the port — the a-sub
  rule's second implementation with zero gate-on coverage, the x-level
  adjacency/downgrade rules living only in non-make-test probes, and
  unset-wins guaranteed only by block order. All three pinned (corpus
  59 -> 67) with sabotage rows S24-26 — and the failing direction was
  measured for free: the rows ran UNDETECTED against the unpinned HEAD
  (mech archives HEAD; the pins were still uncommitted), then DETECTED
  once the pins landed. Mech 23/23 -> 26/26. One predicted figure
  corrected to the measured value ((?-ii) is all unset-side — not a
  contested cell).
- ENGINE: bare `(?` at end of pattern answered "unrecognized character"
  (the 111 family) where PCRE2 gives 114 — and the disposition
  measurement SHARPENED it: `(`, `(?`, `(?i`, `(?^`, `(?-` are ALL 114,
  so the right answer was the one pcrec already gave bare `(`. Fixed in
  ext.c (c2 < 0 answers "missing closing ) for group", both gate states);
  the Q2-era pin moved with its third measured answer in three eras — its
  prose had CLAIMED PCRE2 agreement, unverified for two checkpoints.
  Five clean sweeps recorded as evidence. NOTED: the pre-existing K12
  dash-offset outlier ([z-a]: pcrec pins the dash, libpcre2 the high
  endpoint).
- DOCS: five stale-voice fixes, the worst being tests/modifiers/CLAUDE.md
  reading its watched-failing §9.3 record as CURRENT status — the R16
  failure mode one module later, caught by the same lens. Plus the
  incidental pre-existing noreturn claim (dead since MOD-0.1/K11).
- Panel first: ZERO wrong cells across all three reports — the briefs
  demanded both-sides measurement per claim, and got it.

**MOD-0.5 CLOSES: opened and closed in one session.** The gate measured
first (probe_mod05/b), three parallel subagent lanes (impl worktree,
corpus worktree, D27 cell with a narrowed allowlist), the producers landed
atomically (.5c+.5d, the honest-refusal sequencing ruling), checks moved
with every surface, and the panel's findings were all fixed with
measurement before disposition. The D30 §7 hazard that ordered this
milestone after `classes` — `(?xx)[a- ]` — compiles to members {a,-},
pinned in both gate states, with the lexer rule that decides it
(deletion-aware dash lookahead) carrying its own sabotage row.

Lessons, this session's additions to the catalogue:

- Run new sabotage rows against the unpinned tree first, ON PURPOSE — the
  UNDETECTED/DETECTED pair is the failing-direction validation, free.
- A sweep template that always emits a byte cannot probe the empty/EOF
  boundary — R16's \N lesson recurring at (?%c. Give generators an
  explicit empty row.
- A pin whose prose claims oracle agreement is a measurement claim and
  ages like one; cite the probe, not the belief.
- A corpus block's expectation must be derived from the pattern AS THE
  FORMAT ENCODES IT — the \t-escape block transcribed a raw-byte
  measurement onto an escape spelling (caught at the landing by the
  corpus's own first green run).
- Parallel lanes work when the merges serialize through one reviewer with
  the battery between — and a worker going idle without committing is a
  recoverable state, not a failure: the landing bar travels with the
  brief, so anyone can finish it.

## 2026-08-12 — twelfth session: MOD-0.4 opened and closed (module `verbs`, the migration test)

Frank: commit the new pcrec-manager skill, then begin MOD-0.4; AFK, defer
questions or stop if blocked. Nothing needed a stop.

**The milestone in one line: the doorway signature survived the hardest
case, and the milestone's own marquee hazard — the star=at+1 blame offset —
turned out to be the ONE thing no check guarded.**

- **Session-shape change:** the session ran under the new
  .claude/skills/pcrec-manager skill (committed f88ff2e) — the manager
  workflow (wake -> plan -> brief -> review -> merge -> close) written down
  and followed as written. One read-only scout mapped the verbs surface
  before any design; one impl worktree lane (sonnet) carried all four
  slices through two-phase briefs (design note reviewed BEFORE code);
  three read-only critics closed. Baseline battery green at f88ff2e before
  any milestone work.
- **MOD-0.4a gate** (9aa720a): scope rulings recorded in plan rather than
  probed — PURE migration (no verb produces, the parse.c wall stays), no
  new probe harness (PC-3 IS the live measurement record), RK_VERB stays
  one row (K14's per-name machinery already lives on VerbName). The lane's
  design note raised one real question the brief missed: REFUSE/ext_gate
  would need a second home in mod_verbs.c — ruled option (b), promote to
  internal.h with ONE definition each (the two-homes-drift shape refused).
- **MOD-0.4b, the move** (043d78a, merged 72f4fcf): pcrec_ext_verb + both
  VerbName tables + four accessors -> src/parse/mod_verbs.c with their
  measurement-provenance comments; SEAM IS A DIRECT CALL — doorway 3 has
  ONE row dispatching by NAME, no row family for a recognise pointer, and
  an aport now would wire a producer nothing exercises. The signature
  verdict is DOCUMENTED in the TU header (four table answers via the shared
  REFUSE epilogue, VF_* computation, at==0, star=at+1 — no new vocabulary
  needed). Byte-identity: corpus derived programmatically from baseline
  --list-verbs (resolved the scout's 44 vs the lane's 50 name-count
  disagreement: 50, 31+19), 602 comparisons, zero diffs. Review verified
  the move verbatim by extraction-diff (only the gate rename + one stale
  comment pointer).
- **MOD-0.4c, new guards** (94b0693 + 841d73f landing bar, merged 8f94ccd):
  S27-29. THE FINDING: S27 (blame-offset regression) came back UNDETECTED
  0/437 — the (*) reject pin was message-only and the regression keeps the
  message; closed by pinning "(pattern offset 1)" per the brace family's R7
  convention, both directions measured. S28 52 fails, S29 1 fail (the
  a(*CR) pin), both already-detected. Framework limit recorded: mech has
  no `registry` suite, so PC-3/sweep_verb coverage cannot be mech-claimed.
- **R18 close panel** (f4a9643, docs/reviews/2026-08-12-r18-mod04.md):
  second consecutive ZERO-wrong-cells panel; zero tier-1 divergences.
  CHECKS -> S27's finding generalized to SIX message-only REFUSE families;
  closed same-session (bd9b6a1, merged 19020ee): ten measured offset pins
  (non-zero probes a(*CR)/a(*ACCEPT) at offset 1 for the two
  single-representative families) + S30, whose pre-pin baseline reproduced
  S27's exactly (0/437). ENGINE -> ~35-cell offset-divergence inventory
  vs libpcre2, tier-2 no-action (D26); the star=at+1 and (*:) cells MATCH
  the oracle — now measured claims with citations, not prose; K15 opened:
  >128-byte NON-identifier "names" get too-long where libpcre2 says
  not-recognized (extent scan swallows all but `):=`; verified NOT tier-1),
  a LINKED PAIR with PC-3's identifier-only length generator — the
  sweep-template-misses-the-boundary lesson, third recurrence. DOCS ->
  three live-doc fixes; extension_design §5.3's "(all three already in
  ext.c)" had aged through TWO moves without anyone noticing.
- Close battery green: mech 30/30 (S27 1/436, S28 52/385, S29 1/436, S30
  2/435), reject 268/99/65 + 437 checks, registry_check 167, PC-3 143
  (973,531 verb probes), spec_mod0 12 checks exit 0.

Lessons, this session's additions:

- A milestone that names its own hazard ("a blame offset that is not the
  doorway's default") is naming the thing to CHECK FIRST — the hazard was
  real, and it was the exact cell no pin guarded. Read the milestone's
  plan row as a list of things to verify guards for, not just things to
  preserve.
- An offset regression that keeps the message text is invisible to every
  message-matching pin AND to PC-3 (which never compares offsets) — pin
  offsets wherever the blame position is load-bearing, and let the pins
  claim only pcrec's own stability unless the oracle cell is measured.
- Two-phase briefs (design note -> review -> code) caught the shared-macro
  two-homes hazard before any code existed; the cost was one message
  round-trip.
- A count disagreement between two readers of the same table (44 vs 50
  verb names) is resolved by deriving from the binary's own dump, not by
  re-reading harder.
- The scout->design->brief pipeline preserves main-session context: the
  whole milestone (four slices + panel + close) fit in one session with
  room to spare, where MOD-0.5's shape needed the same. The skill's
  3-lane cap was never hit — one serialized lane was enough for a
  migration; parallelism is for genuinely disjoint work.

## 2026-08-12 — thirteenth session: MOD-0.6 opened/built/closed; K15 ruled and closed; D35; K16 opened at R19

Session ran under /pcrec-manager (the skill's second outing). Frank
present and ruling throughout — five rulings this session. Baseline
battery green at 39f78f9 before any work.

**The milestone in one line: the recogniser landed with zero tier-1
divergences, and BOTH of the project's marquee lessons (S27's
message-only pins, the sweep-template blindness) recurred inside the very
milestone that cites them — caught by mech's first-ever UNDETECTED rows
and by the R19 panel.**

- **K15 closed as ruled** (Frank: acceptable tier-2 + document the
  divergence). Lane landed the linked pair in order: hostile-alphabet
  pool first, PC-3 measured FAILING 78/78 on exactly the K15 cell, THEN
  the narrow exclusion (fires iff rc-160 x over-cap x too-long text) +
  liveness assert (sabotage-validated) + pcre2_compliance.md entry.
  PC-3 143->144. Merged 7b5e494.
- **D35** (Frank): probe OUTPUT reports archived at
  docs/measurements/<probe>.txt via scripts/measure.sh — STABLE filenames
  so re-measurement is a git diff; header stamps date/repo/oracle/gcc.
  REFINED same session (Frank): a report is a PURE FUNCTION of (probe
  blob, ABI blob, oracle version) — all three stamped; `measure.sh
  --stale` answers VALID/STALE with no re-run. Evidence, never an oracle.
  First reports: probe_quant (validation), probe_uprops (at the merge;
  the R19 engine critic reproduced it byte-for-byte — the convention's
  first real validation).
- **MOD-0.6** (Frank's go; ruled recogniser-only — D33 §7 WIDENING
  amendment: defers to the first wide producer). Phase 1 measured before
  design: probe_uprops's 256-byte tail sweep KILLED the plan row's
  predicted finding — \p/\P have NO decline-shaped tail, so the catch-all
  recognise is permanently correct, not the Q2 shape. The 48/49
  significant-char boundary located exactly with the streaming proof
  (blame offset tracks the COUNT, not body length — n=49 blames one past
  the 49th sig char at the same offset whether or not insignificant
  filler doubles the body). Slices: K10 FIXED (flag removal +
  check_class_syntax_reach + 7 pins); mod_uprops.c (streaming scanner,
  PCREC_UPROP_NAME_MAX=48, marker-keyed direct call bypassing aport/cport
  — nothing that refuses may start compiling); 24+3 pins; PC-3
  differential (1,976 probes; 52-letter live-oracle sweep guards the
  hand-written table — manager ruling: hand-written beats generated,
  because generated-from-libpcre2 checked-against-libpcre2 is one source
  wearing two hats); mech S31-S35.
- **Mech's first UNDETECTED rows, working as designed**: S33 and S34 came
  back 0/465. S33's predicted flip misread ruling 3 (a two-char name gets
  the GENERIC message; what MOVES is the caret-prefixed 48/49 boundary)
  — closed with the two caret-boundary pins. S34 was structurally
  undetectable: the buffer's only reader RE-FOLDED on the way in,
  repairing the sabotage — the control-sharing-a-source shape — closed in
  CODE (fold-free uprops_short_lookup; the accumulator's fold is now
  load-bearing) + the \p{c} pin. Also learned twice about the mech
  harness itself: SAB_COUNT is replace.py's anchor-occurrence count (an
  S33 rerun ANOMALY taught that), and run_sabotage_matrix.sh EXITS 0 with
  UNDETECTED/ANOMALY rows — the matrix is a record, not a gate; read
  rows, never the exit code.
- **R19 panel** (docs/reviews/2026-08-12-r19-mod06.md): zero tier-1.
  ENGINE -> **K16 opened** (164/256 \p{...} body bytes are err-146 AT THE
  BYTE to libpcre2; pcrec scans past them — the sweep-template lesson's
  FOURTH recurrence: probe swept the tail byte, census tested four body
  bytes, differential is well-formed-by-construction; all three stop at
  the brace). Frank ruled DEFER to first producer; pins claim pcrec's own
  behavior; compliance entry landed; LINKED PAIR recorded (differential
  stays well-formed-only until the fix). CHECKS -> \p{L}/\P{L} were the
  LAST message-only pins (S27's lesson, fourth recurrence, THREE LINES
  under the comment citing it — fixed); has_eq branch had ZERO coverage
  (manager's own ruling-3 code — pinned); the 1,976-probe differential's
  honest claim is POSITION-INVARIANCE, not absolute offsets (its header
  always said so; closure prose now does too); S31's positive control
  measured to a NUMBER (exactly 1). DOCS -> K10-LIVE staleness + three
  stale "until MOD-0.6's property table" copies + slice-5 lag in
  src/parse/CLAUDE.md — all fixed.
- **Session ops**: THREE lane deaths mid-flight (mod06 twice, mod06b
  once, all while waiting on long test runs); each time the
  landing-bar-travels-with-the-brief rule held and the manager finished
  the landing from worktree state (review-first, then commit). Final
  counts: reject 303/99/65/4 (437->472 total checks), registry_check 168,
  PC-3 154 (verb probes 973,726; uprops 1,976), mech 35/35, corpus/fuzz/
  spec_mod0/bench green.

Lessons, this session's additions:

- Lessons transfer by CHECKLIST, not osmosis: S27's and the
  sweep-template's recurrences were both INSIDE surfaces citing them. The
  close checklist now needs, literally: "sweep the axis your generator
  cannot produce" and "grep the touched surface for message-only pins".
- A sabotage's doc-figure is a PREDICTION and can be wrong two ways: by
  misreading the landed design (S33) and by sabotaging something whose
  only reader repairs it (S34). An UNDETECTED row is the harness working;
  triage the prediction before touching the pins.
- A control must not re-derive what its subject computes (S34's re-fold):
  make the read path TRUST the write path, then sabotage the writer.
- Harness exit codes are not gates unless proven: mech exits 0 on
  UNDETECTED and ANOMALY both. Read the matrix.
- Probe reports as pure functions of stamped dependencies (D35
  refinement) turn "should we re-measure?" into a mechanical --stale
  check — and the first byte-for-byte reproduction validated the whole
  convention.

## 2026-08-12 — fourteenth session, opening item: the "make mech silently stopping" report — not a crash; the liveness poll was lying

Frank opened the session reporting `make mech` had "silently stopped"
twice without the manager noticing, cause unknown. Investigated from
three evidence sources (leftover scratch roots, the thirteenth session's
transcript, kernel logs) before touching anything.

**Finding: every mech run yesterday COMPLETED.** All 34 leftover scratch
roots across /tmp and /var/tmp held complete row sets for the sabotage
listing as it existed at their moment (20→23→26→29→30→35 rows tracking
S21–S35's landings); no abandoned sabotage trees; no OOM kills. What
stopped silently was the session's BELIEF: the S31–S35 validation run
finished at 16:53 (`MECH_RC=0`, 35/35 rows), but the lane that launched
it had died — taking the background task's completion notification with
it — and the manager's outside-in liveness poll, `pgrep -f "make mech"`,
answered MECH_RUNNING at 17:44 and MECH_ALIVE at 17:49, 51+ minutes
after completion. Root cause: the session harness wraps every polling
command in a `/bin/bash -c 'source snapshot… <command>'` whose own
command line contains the pattern, so the poll matches ITSELF —
reproduced live this session (`pgrep -af "make mech"` with nothing
running: one match, the wrapper). The 17:49 `ps --forest` had even shown
it (the "make mech" pid: STAT Ss, ELAPSED 00:00) and it went unread.
This is the check-design lesson in a new costume: a control sharing a
source (the literal string "make mech") with its subject.

**Fix, landed this commit:**

- `run_sabotage_matrix.sh` now ends every successful run with a
  grep-able completion trailer — `== mech run COMPLETE: <N> rows
  (undetected: U, anomalies: A) at <SHA> ==` — so "is it done" is
  answered from the log artifact. The only early exit that skips it is
  the loud FATAL path. Watchers grep for `COMPLETE|FATAL`, never pgrep.
- The run now removes its mktemp'd scratch root and parallel-mode row
  dir on exit (KEEP=1 preserves; a caller-supplied MECH_SCRATCH is never
  removed) — yesterday's 34 leftover roots were this hygiene gap; swept
  them after mining them as evidence.
- tests/mech/CLAUDE.md documents the trailer and the pgrep trap.
- Validated: single-sabotage run (S15) prints the trailer, DETECTED
  12fail/459pass, scratch root gone afterward.

Lesson (also added to the check-design memory): a liveness poll whose
pattern names its target matches itself through the harness wrapper;
completion of a long run is a fact about its output artifact, and a dead
lane silently discards its tasks' completion notifications — read the
file, not the process table.

## 2026-08-12 — fourteenth session: MOD-0.7, `--explain` rewritten — and the milestone's own cure refuted before it was built

**MOD-0.7a (design note) then MOD-0.7b (six slices), both complete.**
`docs/design_notes_mod07.md` is the record; this entry is the part a
restarting reader needs.

**The headline is a refutation of the plan row's own instruction.** [MOD-0.7]
said: print the row's declared attribution and the recogniser's answer and
assert they agree per row. Applied literally that cannot catch a module
swap, because `ext.c` renders "requires module '%s'" from the same
`r->module` `--explain` prints. Measured before anything was designed:
R10/C4-1's sabotage applied at `26b9660`, then the whole 100-row
declared-vs-live census re-run — **93 SAME / 6 SILENT / 1 NOROUTE, bit
identical to the correct table**, both swapped rows still reading "SAME".
Suite-wide detection of that swap, each suite run alone because `make test`
halts at the first failure: `tests/reject` 2 (hand pins), case10 1 (the
`--count-groups` pin), `registry_check` + `pcre2_check` **0 of 322**, the
committed doc index 1. **All eight of case10's `--explain` assertions passed.**

So the live call was kept for what it does deliver — ELECTION (13 rows share
their rendered diagnostic with a bucket sibling, so text cannot say which
answered) and PROMISE CONSISTENCY — and module-name truth stayed where it
already lived, in hand-written pins.

**A live defect, found by applying the design to its first row.**
`--explain '(?C1)'` promised module `callouts` while the compiler said "no
module will implement it". K14's over-promise, fixed in `ext.c` at MOD-0.1 and
rendered correctly by `put_expect` 100 lines above in the same file since the
same milestone; `--explain` never read `roadmap`. D26 tier 2 in D26's own
words. One row today. Fixed here under the manager's FIX-3 ruling — pin
written first, run against the pre-fix rewrite, **recorded failing** (one
assertion, 182 pass / 1 fail), then the fix. No K number: found and fixed
inside one milestone.

**And the same lesson recurred INSIDE the milestone that found it.** The
`agree` clause cannot see the `(?C1)` defect either — both of its sides read
the row, so the live answer (correctly promising nothing) and the declared
columns agree while the rendered sentence lies. Only the hand-written pin
catches it. Twice in one milestone: a control fed from the thing it controls
reports agreement, and agreement is not correctness.

**What landed, in slices:** one doorway router shared by `--probe-ask` and
`--explain` (1089 cells byte-identical, check06 floors unmoved);
`ExtResult.row`, stamped by a thin wrapper per doorway so a later `return`
cannot forget it (876 compile cells byte-identical); the rewrite — a query is
TEXT AT A DOORWAY, selection is prefix ∪ bucket-candidates with each row
tagged, the query's live answer is DATA and each row's canonical live answer
is the ASSERTION, exit 3 for a dissent; cli case11, 63 field-level assertions
under a stated no-`assert_contains` rule, with case10's eight blob assertions
DELETED rather than duplicated; V1-V7 measured; docs.

**Two harness bugs worth remembering, both found writing the case.**
`awk -v row='\v'` processes escape sequences in the value, so half the rows
arrived as a vertical tab and matched nothing — pass row/key through the
ENVIRONMENT. And a sweep loop that matched `agree` lines by fixed column
reported 81 dissents on a clean table the moment a key got one space wider:
match on the KEY and trim, never on padding.

**Deferred, with reasons:** the normalised `\p` name waits for the first
`unicode-props` producer (manager ruling 2, superseding the plan row's
wording — K16's linked-pair logic: accessor, consumer and K16 fix land
together). In-class routing for `--explain '[\p{L}]'` and a `mech` `cli`
suite arm are MOD-0.8 candidates; the mech arm's CODE is trivial and its
RUNTIME is unmeasured, which is the reason it is not built.

**Named for the next reader (§9.4):** case11's query set is HAND-LISTED. The
generated query space is not swept, so a routing or selection bug affecting
only a byte outside that list is invisible to it. That is the sweep-template
lesson's fifth possible recurrence and this is its signpost.

## 2026-08-12/13 — fourteenth session: mech liveness diagnosis; MOD-0.7 open-to-close; MOD-0.8 checkpoint (R20 + D27) — TWO tier-1s found and fixed; MOD-0 ARC CLOSED

Session ran under /pcrec-manager, Frank present and ruling throughout
(default-on, callouts re-scope, xmas rows, gate principle, SR-10, SAN-1,
TT-1, queue discipline — eleven rulings). Baseline green at 26b9660.

**Opening item — Frank's report "make mech silently stopping, unnoticed
twice": NOT a crash.** Every mech run had completed; the thirteenth
session's liveness poll `pgrep -f "make mech"` matches its own harness
wrapper and answers RUNNING forever (reproduced live). Fixed at the
artifact level: mech runs now end with a grep-able `== mech run COMPLETE ==`
trailer + scratch cleanup (26b9660). The lesson later completed its pair:
this manager ALSO made the opposite call — judged a live lane dead
(ListAgents empty while it was blocked in a foreground make test) and
briefly meddled in its worktree (disclosed, repaired, no loss). Frank's
directive closes the root cause: SUBAGENTS RUN LONG VALIDATION
ASYNCHRONOUSLY (background + artifact polling, never a blocking foreground
call) — in root CLAUDE.md, the manager skill, and memory (60711b2).

**MOD-0.7 (--explain rewrite), open to close in one arc (b2cecc8):**
- Phase-1 design note REFUTED the plan row's own cure before building it:
  the declared-vs-live agreement clause is SWAP-BLIND (both sides read
  r->module) — measured both directions; and found a live tier-2 on main
  ((?C1) promised module 'callouts' against ROADMAP_NEVER — syntax_dump
  never read the K14 column). Design reshaped: hand pins own module-name
  truth; the live call earns its place on ELECTION (13 rows share a
  rendered diagnostic with a bucket sibling) and promise-consistency.
- Six slices: shared doorway router (--probe-ask byte-identical, 1,089
  cells), ExtResult.row (876-cell compile differential, zero diff),
  the rewrite (selection = prefix ∪ candidates tagged; live-on-query is
  DATA, live-on-row-syntax is the assertion; exit 3 = dissent), case11
  (field-level, no blob assertions, (?C1) fixed FIX-3-style with the pin
  recorded failing), V1-V7 failing-direction measurements, docs.
- Manager rulings §13: normalised name DEFERRED to first uprops producer
  (K16 pair); class-position stays declared; verb sub-block kept; exit 3.

**MOD-0.8 checkpoint — R20 panel (3 critics) + D27 blinded writer:**
- R20 findings (docs/reviews/2026-08-12-r20-mod08.md): TIER-1 —
  probe/explain surfaces longjmp into an uninitialized jmp_buf once a
  producing module is enabled (inherited from MOD-0.3c/0.5c; the extracted
  function CARRIED the comment naming the overdue obligation). Two tier-2
  clause defects on the gate axis the census never varied ((?J)/(?m) false
  DISSENT exit 3; clauses silently off for producing rows). ExtResult.row
  NULL-contract false on two decline paths. OPTRUN: (?P truncation (the
  sweep-template lesson's FIFTH recurrence — the tail template cannot
  generate the zero-tail cell); ~513M probes otherwise unrefuted; measured
  boundaries B1-B4. Docs: three staleness fixes (067c024).
- D27 blinded writer (cell spec-mod08): **TIER-1 MISCOMPILE — `a(?i)*`
  accepted and compiled with modifiers enabled, quantifier bound to the
  preceding atom; libpcre2 err 109.** The registry always said these rows'
  quantifiable is `form`; the producer contradicted it. check11 (hand-listed
  21 spellings, none quantified) owned the module and missed it — D27's
  wager paid a SECOND time, one level in: the GENERATED sweep reached the
  cell, not source-blindness alone. Checks 13+14 (7,294 cells) landed loud
  RED as the false-the-day-before record; green after the fix merged.
- mod08fix lane, six slices (db7ad1c): setjmp guard (5,080-probe sweep
  18→0 crashes); clauses scoped to the CLOSED gate + new gate clause
  (100×5 census all-zero); NULL biconditional; (?P fix (1 of 255 truncated
  cells moved) + tail sweep truncated halves (10,200→20,400 — first
  version was OR-vacuous, self-caught, split); tier-3 batch; SPEC-1 fix
  (not_repeatable flag; \E/(?#) transparency oracle-verified unchanged;
  11 offset pins). Its slice-3 "328 patterns" figure was locale-collapsed
  (sort -u); superseded by the 3,069-pattern differential — do not cite.
- mod08c lane, four slices (569b48f): mech registry/pc3/cli arms (costs
  measured FIRST: 0.60/4.36/5.46s vs reject's 54.75s; pc3 skip
  failing-direction validated, INCONCLUSIVE-never-UNDETECTED, trailer
  counts pc3-skipped); **S19's documented blind spot closed AND found
  stale in two directions** — it had already become DETECTED (reject row
  count) with nobody noticing, and the pc3 arm adds an external answer
  (libpcre2 has no \j); PC-3 FOCUSED gated pass per Frank's differential
  gate principle (49,034 cells, T1 clause, modifiers-only ==
  --features-all byte-identical so focusing is free; SPEC-1 revert lights
  672 gated cells while all closed-gate PC-3 stays green); -e utf8 reworded
  to milestone phrasing (case13; the -e gate had ZERO coverage repo-wide);
  deferred-validation ordering documented (142 closed-gate → 8 open-gate
  deferring cells — "population only shrinks" measured).

**Frank's rulings shelf (all recorded in plan/decisions):** D36 callouts
NEVER→PLANNED (M4-hosted, static extern binding, V-A trampoline composes);
D37 default-on via FROZEN NAMED SETS (std1={classes,modifiers}, stamped
artifacts, bare default advances only at announced boundaries) + [STD1]
implementation row; differential gate principle (testing.md); [SR-10]
single namespace tables; [M4-SUBST] compiled substitution (template
compiler independent of the matcher — Frank's observation — compile-time
group-reference checking); V-A gains the POSIX regex.h shim; [V-E]
multi-pattern units + cross-pattern finder (OS-0's first customer);
[V-F] source-scan transformer (regular marker grammar as the design
constraint); [SAN-1] sanitizer+lint battery BOTH axes (compiler and
compilee via GENCFLAGS) before OPT-A; [TT-1] tiered testing (make test
never weakens; CI deferred-not-rejected with named triggers); queue
discipline (boonies tier well after the M3-M7 spine).

**Final state (569b48f, battery green):** corpus 1270, cli 221 (case11 88,
case12 14, case13 7), reject 486 (306/99/65/0/15 gated), registry_check
168, PC-3 163 (gated[modifiers] pass; tail sweeps 20,400), spec_mod0 14/14
(checks 13+14: 7,294 cells), codegen 29, trie 7, thread green, mech 35/35
(0 undetected, 0 anomalies, 0 pc3-skipped), strict clean. **MOD-0 CLOSED.**

Lessons, this session's additions (full statements in the memory file):
- A liveness probe whose pattern names its target matches ITSELF through
  the harness wrapper — and the belief error has a mirror twin (live lane
  judged dead). Poll artifacts; async validation for subagents; check
  worktree mtimes + message before finishing an "idle" lane's landing.
- A carried-forward comment is a carried-forward OBLIGATION: the tier-1
  crash sat exactly where an extracted function's own comment said "the
  first producing port must revisit this" — two milestones overdue.
- An axis your census never varied is an axis your clauses are wrong
  about (the gate; both tier-2 clause defects).
- A documented expected-UNDETECTED is a claim with an EXPIRY DATE and
  nothing was checking it (S19, stale in both directions).
- The generated sweep, not source-blindness alone, is what makes D27 pay:
  a hand-listed probe table inherits its author's alphabet whether or not
  that author could read the implementation.

## 2026-08-13 — fifteenth session: TT-1 + SAN-1 both landed; box reboot mid-session, zero loss; battery placement ruled

Session under /pcrec-manager, Frank present intermittently; light session
as ordered, exactly the queued pair, both closed. Two SONNET worker lanes
(Frank: lower models, subscription limits), concurrent, merges serialized.
Baseline verified green at 662c528 before lanes launched.

**[TT-1] tiered testing (lane tt1, merged c9776ee):** 9 section targets
wrapping `test:`'s own scripts (`test:` byte-untouched; test-spec wrapped
though deliberately not part of make test — documented three places);
`make smoke` = 6 fast sections, 31-32s across 3 runs, SMOKE_FLOOR=6 a
literal independent of SMOKE_SECTIONS (check-design lesson applied),
floor sabotage-validated (dropped section → loud trip, exit 2, restored);
per-section runtimes measured 3x with per-run load sampling after the
lane's FIRST sweep was discarded whole for R3.10 contamination (overlapped
san1's runs; single-sample load check — the exact historical mistake);
touched-path→sections table; doubling re-record trigger; opt-in `make
hooks` pre-push resolving `git rev-parse --git-path hooks`. Corpus is
~304s of ~391s serial total — the tier structure was visible in the data.

**[SAN-1] sanitizer+lint battery (lane san1 + manager landing, merged
f943060):** make ubsan/asan/lint, opt-in, BUILD_DIR-separated trees, BOTH
axes. Headline: the GENCFLAGS COMPILE-SITE AUDIT found FIVE deaf sites
(cli, pc4, registry-link, parse-link, trie_identity $REF) — the compilee
axis was silently partial its whole life; new hooks LIBPCREC/SANFLAGS/
LINTGEN plumb them. Frank's LINTGEN=1 "2-fer" rides make test's own
compile pass with -fanalyzer: +53.7s/+13.8% quiet-measured; 9-shape
false-positive survey first (zero, incl. computed-goto trie). Four
sabotage validations (both sanitizers x both axes) fired. F1: -Wclobbered
on pcrec_syntax_explain's rows_shown/dissents, asan-build only —
manager-triaged BENIGN (handler reads neither; comment already stated the
invariant), hardened volatile (2e71606). Gotcha recorded: -O1 DSE legally
erases an unobserved heap-overflow write before ASan sees it. Quiet
runtimes (serial, idle box, per-run load ≤1.05): baseline test 389.7s
(agrees with TT-1's independent ~391s section-sum), LINTGEN 443.3s,
ubsan 408.9s, asan 470.4s (green post-F1), lint 8.8s. Contended earlier
figures superseded; they landed within ~7% of quiet — discipline kept
anyway. SANFLAGS-on-$REF coupling RULED KEPT (F1 is its existence proof).

**Battery placement RULED (manager, from the numbers, in testing.md):**
merge/close battery gains ubsan+asan+lint; battery-grade make test adopts
LINTGEN=1; smoke never; asan red blocks a merge like a test red.

**Incidents, all recovered:** (1) cross-lane timing contamination —
caught, sweep discarded, measurement windows then explicitly serialized
by the manager. (2) tt1's Monitor missed its sweep-completion wake twice
(Frank spotted the idle box once); a 10-minute manager cron doing
ARTIFACT-based stall checks (worktree mtimes + log trailers,
message-first) covered the rest of the session; deleted at close.
(3) THE BOX REBOOTED 02:50 (journalctl -b -1: clean systemd shutdown,
not a panic; external cause) — both lane agents died, ZERO work lost:
tt1 already merged; san1 had committed everything after a manager nudge
~40min earlier ("commit as you go" is crash insurance, measured). Manager
finished san1's landing per protocol (quiet re-times + docs + rulings).

**Also this session:** browser/Wasm backend discussed, left CONVERSATIONAL
per Frank (no plan row); assessment + cheap first experiment recorded in
wake.md §1. Stale mod08c worktree cleaned. tt1 fixed two pre-existing doc
staleness bugs (tests/thread/CLAUDE.md make-test claim; tests/CLAUDE.md
missing spec_mod0/ + mech/ entries).

**Close battery at e2ee3a1, ALL GREEN:** strict 2.7s; test LINTGEN=1
PROCS=6 157.2s; spec 14/14 25.5s; fuzz seed-1 4.5s; ubsan 411.2s green
both axes; asan 474.6s green both axes; lint 8.8s clean; bench 15.0s;
mech 266.6s trailer `35 rows (undetected: 0, anomalies: 0, pc3-skipped:
0)`. Counts unchanged (infrastructure session, no new test rows).
Worktrees tt1/san1 removed post-merge; only d27-selftest-cell remains.

## 2026-08-13 — sixteenth session: docs tree reorganized; plan split + development order ratified; PC-5/BENCH-1 rows added (no code)

Planning/documentation session, Frank present and ruling throughout. No
src/, cli/, lib/ or test changes; the suite is untouched. Two `make smoke`
runs green (6/6 floor) around the merges; the full battery was deliberately
NOT run (doc-only session) — the standing baseline verification remains the
fifteenth-session close battery at e2ee3a1.

1. DEVELOPMENT ORDER RATIFIED (Frank): **STD1 → M4 (captures + VM) →
   M5 (UTF-8) → M6 (feature modules) → M3 (streaming) → M7 (hardening).**
   Frank challenged M3-streaming-next (the old numeric order) as less
   fundamental than the VM and classes; manager analysis concurred with one
   correction — classes/modifiers already exist as gated modules (MOD-0.3/
   0.5; [STD1] flips the default) — and moved streaming late on the
   rebuild-risk argument: a `*_stream_*` API built now binds to the DFA
   engine only and gets forked or rebuilt when the VM (M4) and
   lookbehind/backrefs (M6) change what a stream window must retain; OS-3
   already predicts streaming is not a wrapper. M5 sits before M6 so
   feature modules are born CharSet/UTF-aware (DD-12, DD-1) rather than
   rebuilt. The backrefs/atomic/subst-template design notes precede M4
   (its design customers); MECH-3 precedes OPT-A. Encoded in plan.md's new
   "Development order" section.

2. DOCS TREE REORGANIZED (lane docs-reorg, sonnet, worktree; merged
   5196500): `docs/dev/` = process docs (plan.md, plan_completed.md,
   dev_journal.md, decisions.md, known/upstream issues, reviews/, wake.md
   untracked); `docs/design/` = living design docs (extension_design, the
   mod06/mod07 notes, design_registry_selectors); `docs/spec/` = NEW,
   empty except its charter CLAUDE.md (spec docs = how the tool actually
   works and how to use it; deliverables like code, maintained, no build
   history; may cite design docs — none authored yet; testing.md is a
   future candidate but carries build history and stays in docs/ for now).
   testing.md, pcre2_compliance.md, measurements/ stay in docs/. 89 files
   relinked; dev_journal.md and reviews/ content deliberately untouched
   (historical citations stay as written). Smoke green in the worktree
   before merge. Memory files and the pcrec-manager skill updated to the
   new paths.

3. PLAN SPLIT + REORDER (lane plan-restruct, sonnet, worktree; merged
   c932c82): `plan_completed.md` archives 91 completed rows verbatim,
   grouped by completion date (2026-08-09 → 08-13; MOD-0 arc contiguous
   under its close date). Active plan.md now 45 rows (42 not-started,
   3 deferred: DOC-BM, SR-7, SR-8), zero completed, restructured to the
   spine order with `## Next: [STD1]`, the backrefs/atomic design notes
   relocated under M4, boonies at the tail, and a small-debt shelf
   (pointers only, no STATE tags). Hygiene fixes: the completed
   make-strict row renamed [MECH-STRICT] (its "[MECH-3]" id collided with
   the active measurement-wrapper row); [MOD-STATE] flipped to
   completed-RETIRED (subsumed by Part II §12.2 / MOD-0.1 slice 7).
   ID conservation verified: 133 old top-level rows == 136 new minus the
   3 deliberate additions ([STD1] promoted from nested text, [PC-5],
   [BENCH-1]); no id lives in both files.

4. NEW PLAN ROWS (Frank's rulings this session):
   - **[PC-5]** PCRE2 option/flag disposition survey — flag-by-flag
     sibling of pcre2_compliance.md with a binding-time vocabulary
     (DONE-AS / RIDES / GENERATION-AXIS / API-PARAM / EMITTED-LOOP /
     LATER / NEVER-with-reason); fact-gathering is lane work, dispositions
     are Frank's; the table must exist before M4's match-API design
     freezes; output docs/pcre2_options.md.
   - **[BENCH-1]** feature-spanning benchmark expansion + the PRIORITIZER —
     per-feature-family case groups at graded complexity, spot-checkable
     like TT-1's tiers; the regression gate stays absolute per-case floors
     (M2.11's ruling), the prioritizer is a separate relative-vs-libpcre2
     worst-first ranking, informational and never a gate; rides M7's
     testdata import; it is the OPT waves' worklist generator (Frank's
     workflow: OPT-A survey, then work the ranking worst-first).

5. Flags discussion on record (PC-5's seed): the AOT binding-time framing —
   pattern-semantics options are modifier letters / generation scalars
   (mostly done or scheduled); match-time options are really M4 API design
   (ANCHORED → compiled variant, NOTBOL/NOTEOL → runtime params,
   NOTEMPTY(_ATSTART) → subsumed when pcrec emits the global-iteration
   loop itself at DD-4/M4-SUBST); engine-behavior knobs are mostly moot
   for an AOT compiler; NEWLINE/BSR belong to DD-11; the EXTRA_* tail is
   DOC-BM's territory.

6. Incident, recovered: two Frank-ruled row additions were SendMessage'd
   to the plan-restruct lane MID-FLIGHT and landed after it had already
   committed and reported — its invariant summary (43 rows, "one
   addition") contradicted the expected additions, which is exactly how
   the gap was caught; a resume message applied both rows and re-verified
   (45 rows). Lesson: read a lane's report invariants as a RECEIPT for
   everything sent to it; anything sent mid-flight needs explicit
   confirmation it was processed, because a lane can finish between your
   send and its read.

Next steps: [STD1] awaits Frank's go and a roomy session (unchanged).
PC-5/BENCH-1 fact-gathering are schedulable as lanes whenever Frank wants
the tables. Nothing in flight; zero STATE:started rows. Worktrees
docs-reorg/plan-restruct removed post-merge; only d27-selftest-cell
remains.

### Sixteenth session, late addendum — positioning ruled and recorded

Frank ruled the niche discussion RECORDED (post-close, same session). What
landed, all in docs/dev/plan.md: a POSITIONING NOTE at the head of Beyond
M7 (the one-sentence niche: PCRE2 semantics, compiled to verified,
dependency-free C — fastest where the pattern is known ahead of time, the
only one with compiled substitution; five elements each tied to an owner
row; re2c named as the embedded incumbent; the verification story named a
product feature); [BENCH-1] amended with a latency/short-subject case
group (time-to-first-match from process start, per-call overhead on short
subjects) and the prioritizer's second reading (best cells feed
positioning, worst cells feed fixes); [M4-SUBST] amended with the
beyond-PCRE2 direction (shell-style transforms, C-callback template
segments reusing M4-CALLOUTS' static-extern primitive, own-namespace
discipline per SR-10 so D26's compat story stays clean); [V-E] annotated
as the answer to two use-case questions (organizing/finding compiled
matchers = the finder; the manifest = the user-facing regex-specification
FILE FORMAT, to be designed as a first-class surface); and two NEW boonies
rows — [V-G] user-facing regex testing (package the .rxt harness + oracle
differentials as a `pcrec test` surface) and [V-H] debug/trace emission
modes (traced matcher variant + verbose compile narration; DD-8 keeps
--emit-ir/--emit-dot). Frank's other two use-case ideas already had rows:
the rx/.../ source scanner is [V-F], the organizing system is [V-E]. All
boonies-tier by his word — parking spots, not queue positions.

## 2026-08-13 — Seventeenth session: [STD1] started (D37 implementation)

Frank's go received. Session constraint on record: near subscription
limits; worst case the tail finishes tomorrow with sessions left open —
therefore DOUBLED JOURNALING (an entry at every phase boundary, not just
session close) so an interruption loses nothing.

Session shape ratified in discussion (this session, pre-start):
1. Sonnet implementation lane (worktree std1-impl): named-set table
   (std1 = {classes, modifiers}), --features std1|none|<explicit>,
   bare-default -> std1 mapping, artifact stamping (set name + expanded
   module list in emitted header + macro). Small, spec'd by D37.
2. Merge + battery, THEN re-baseline fans out (re-baseline needs the
   flipped default to test against — lanes are sequenced, not parallel
   with impl).
3. Two sonnet re-baseline lanes: (a) reject_gated inversions + corpus
   features-directive sweep, (b) PC-3 gate state + check07 equivalence.
4. check09 per-name arming + check01 aperture/floors: DESIGN stays at
   manager level (memory: every pcrec check has failed via control
   sharing a source with what it controls); sonnet implements the
   written spec; sabotage validation before either check counts.

[STD1] plan row flipped to STATE:started. Worktree std1-impl created at
5c218bd. Baseline: fifteenth-session close battery at e2ee3a1, smoke
green through session sixteen; counts corpus 1270 / cli 221 / reject 486
/ registry 168 / PC-3 163 / spec_mod0 14 / codegen 29 / mech 35.

### Seventeenth session, phase boundary 1 (doubled-journaling entry)

Impl lane (sonnet, worktree std1-impl) briefed and running: named-set
table + --features std1|none plumbing + artifact stamping, bare default
DELIBERATELY kept empty in phase A (the flip travels with the re-baseline
so every merge stays green). Landing bar includes byte-identity proof for
bare-default invocations.

Manager work while lane runs: phase C check re-arm spec WRITTEN to
docs/dev/std1_check_rearm.md (delete/archive at STD1 close). Key verified
premise recorded there: check07 passes explicit --features on every
invocation (lines 311/408) — the flip does NOT change its semantics;
phase C re-arms check09 (per-name floors in floors.txt + set-membership
honesty assertion against the stamp) and check01 (aperture widened to
phase A's new symbols, isolation extended over them, discovery floors),
each with named sabotage validations. check07's rule changes: none.

Session state if interrupted here: impl lane may still be running or done
(check worktrees/std1-impl for commits on branch std1-impl); nothing
merged; main-tree changes so far: plan.md STD1 STATE:started, this
journal, the rearm spec file (all uncommitted).

### Seventeenth session, phase boundary 2 — STD1a rulings (doubled-journaling entry)

Impl lane reported (work done, make test in flight, uncommitted). Three
judgment calls ruled: (1) artifact stamp is UNCONDITIONAL, bare
invocations included — lane's D37 reading beat the brief's literal
byte-identity invariant (an unstamped bare artifact is exactly the one
that cannot self-describe; skip-when-bare would tie stamp presence to
invocation spelling). Amended phase A invariant: matcher-code identity,
delta = stamp lines only — demonstrated over 5 probe patterns x 3
emission modes against a 5c218bd build. (2) case10's pre-existing
"--features all byte-identical" assertion, invalidated by the stamp by
design, re-shaped to skip the 4 stamp lines + companion stamp-differs
assertion — accepted as a travelling re-baseline. (3) plan.md hunk
reverted by lane (manager-owned); phase split recorded by manager as
STD1a/b/c substeps instead. Expected counts at STD1a merge: cli 221->242,
codegen 29->33, all else baseline. Library-side named-set resolution
(enabled.c, one name->bits lookup) accepted as following the code's grain.

State if interrupted here: STD1a uncommitted in worktrees/std1-impl,
make test running in lane; on green, lane commits and reports; merge +
battery is next manager action. STD1b/c not started; rearm spec at
docs/dev/std1_check_rearm.md.

### Seventeenth session, phase boundary 3 — STD1a merged, flip cut, STD1b lanes out

STD1a MERGED to main (merge 3048303; lane commit 30461a4; manager docs
commit 0dca4a7 before it). Full make test + strict green in the lane's
worktree at the merged code state (corpus 1270, cli 242, reject 486,
registry 168, PC-3 163, codegen 33, trie 7, thread 8, known_fail empty);
post-merge main verified by build + make smoke 6/6. Full battery
(ubsan/asan/lint/bench/mech) deliberately deferred to STD1 close, which
re-runs everything post-flip anyway. Worktree std1-impl removed.

THE FLIP is cut as ab7592d on branch std1-flip (NOT on main):
PCREC_DEFAULT_FEATURES "none"->"std1" + help-text/comment coherence,
manager-authored. Verified: bare '\d+' now compiles and stamps
"std1 (modules: classes,modifiers)". main stays green; std1-flip is
expected-red until re-baseline.

STD1b lanes spawned (both sonnet, branched from ab7592d):
- std1-rebase-tests (worktree same name): reject/corpus/cli/codegen
  territory, coverage-conservation rule (inverted rows keep refusal
  pinned under --features none AND gain oracle-verified bare-accepts
  coverage).
- std1-rebase-oracle (worktree same name): registry/PC-3/spec_mod0
  territory; floors may ratchet up, never down; STD1c re-arm explicitly
  out of its scope (spec: docs/dev/std1_check_rearm.md).
Both run validation async at PROCS=3 (concurrent lanes sharing the box).

State if interrupted here: main green at 3048303 incl. STD1a; flip at
ab7592d (std1-flip branch); two lanes possibly mid-work in
worktrees/std1-rebase-{tests,oracle} — check their branches for commits
and the lanes' worktree mtimes before finishing their landings. Merge
order when they land: lanes -> std1-flip -> full make test -> main.

### Seventeenth session, phase boundary 4 — oracle lane landed (doubled-journaling entry)

std1-rebase-oracle reported and committed (22e3305): registry 168 +
PC-3 163 + pc4 62872 cells all flip-immune WITH the mechanism confirmed,
not just the outcome — tests/registry links libpcrec.a and never calls
pcrec_enabled_set_spec, so it runs at the library's raw EMPTY mask. That
TWO-DEFAULTS fact (CLI bare default = std1; library raw default = empty,
by D20's not-an-option ruling) is recorded as a dated D37 addendum in
decisions.md; the library-channel default question re-opens with D20's
promotion, not before. tests/parse 8/8 unaffected. spec_mod0: 13/14
flip-immune (check02 is the one bare-default consumer by design);
capture.pcrec_compared floor raised 1->5 by the lane;
capture.pcrec_refused 101->97 LOWERED BY MANAGER REVIEW (b1d3231 in the
oracle worktree) — population conserved at 102 (5+97==1+101), rows moved
INTO the compared bucket; the one legitimate lowering shape. Lane
correctly refused to lower it itself. check07 measured post-flip:
eligible_rows 22 (floor 12), baseline_accepted 23 (floor 13) — ratchet
raises assigned to STD1c (noted in std1_check_rearm.md). Verification
spec_mod0 re-run in background at boundary time.

State if interrupted here: oracle branch ready at b1d3231 (worktree
std1-rebase-oracle); tests lane still working (worktree
std1-rebase-tests); merge order unchanged: both lanes -> std1-flip ->
full make test -> main. decisions.md D37 addendum + rearm-spec update +
this entry are uncommitted on main.

### Seventeenth session — composition proposals recorded (Frank's ruling)

Side-conversation proposals RECORDED per Frank, syntax and semantic
choices explicitly TBD (his): [M4-CALLOUTS] amended with the callout-ABI/
match-here alignment proposal (decide before M4 match-API freeze — same
gate as PC-5; atomicity + DFA-islands semantics noted; tension with the
pcre2_callout_block mirror to resolve at design time, V-A trampoline the
candidate reconciliation). [V-E] amended with manifest NAMED DEFINITIONS
+ cross-references (two composition tiers: source-level AST inlining
default, link-level callout ABI; the open PCRE2-(?(DEFINE))-desugar vs
own-spelling choice recorded as Q2/K4-tier measured-not-read; cycles
rejected cleanly; re2c/flex parity note). [V-G] amended: subpart testing
rides V-E's named definitions. All boonies tier, no queue changes.
### Seventeenth session, phase boundary 5 — STD1b lanes merged, integration gate running

std1-rebase-tests landed (6ef0c5d, reviewed and approved): coverage
conservation held throughout — ~32 hand-written reject rows inverted with
old bare behaviour re-pinned verbatim under --features none + new accept
controls; SR-4 iterated loop now probes classes/modifiers rows under
--features none (the flip made a bare probe silently assert against
dissenting per-letter attribution); case14 rewritten to bare==std1
byte-IDENTITY incl. stamp; 3 other broken bare invocations in cli cases
10/11/12 fixed with --features none; codegen bare-stamp check flipped to
std1 + new none-stamps-none check. Counts: corpus 1270->1284, cli
242->247, codegen 33->34, reject 528 checks (gated 15->55, accepts
65->99). Lane independently re-derived the two-defaults fact via
tests/thread/ts3_driver.c (library-linked, unaffected by the CLI flip) —
consistent with the oracle lane and the D37 addendum. It flagged
docs/pcre2_compliance.md's ~15 OK-GATED rows stale.

Both lane branches merged into std1-flip (5eebbed oracle, 09f0535
tests; disjoint, no conflicts). INTEGRATION GATE now running async on
std1-flip: full make test (PROCS=6) + spec_mod0, log
scratchpad/integration_test.log, watcher set. Concurrently: sonnet lane
std1-compliance (worktree std1-compliance off 09f0535) updating
pcre2_compliance.md's stale gated rows against the live merged binary.

State if interrupted here: std1-flip at 09f0535 holds the entire STD1b
landing; main still pre-flip green at 0e89506. On integration green +
compliance lane merge: std1-flip -> main, then STD1c per
std1_check_rearm.md, then close battery + STD1 completion bookkeeping.

### Seventeenth session, phase boundary 6 — INTEGRATION GATE GREEN, STD1c launched

Integration run on std1-flip @ 09f0535: make test EXIT 0 + spec_mod0
EXIT 0, all 14 spec checks, counts at the new baseline (corpus 1284, cli
247, reject 274 rejections / 528 checks, codegen 34, registry 168 + PC-3
163, trie 7, thread 8/8, known_fail empty). The combined STD1b landing
(flip + both re-baselines + floor ruling) is verified as a composition,
not just lane-by-lane.

STD1c lane (sonnet, worktree std1-rearm, branch std1-rearm off 09f0535)
spawned against docs/dev/std1_check_rearm.md as the governing contract:
per-name gate.pairs floors measured-not-guessed, compared_pairs 0->
measured, eligible/baseline ratchets 12->22 / 13->23, check01 aperture
widened from nm over the merged build, five sabotage validations
evidence-required. Compliance lane (std1-compliance) still working on
pcre2_compliance.md's stale gated rows.

State if interrupted here: std1-flip @ 09f0535 verified green; main
still pre-flip at 0e89506. Two lanes in flight: std1-compliance (docs),
std1-rearm (STD1c). Merge order: both lanes -> std1-flip (spec_mod0
re-run after rearm merge) -> main; then plan states (STD1a/b/c
completed), close battery, wake.md rewrite.

### Seventeenth session — compliance lane merged (2aebe8b on std1-flip)

pcre2_compliance.md re-baselined: 9 OK-GATED rows -> OK under the std1
default (all 28 constructs verified against the live merged binary, both
bare and --features none), OK-GATED status definition updated to D37
vocabulary, headline reject counts MEASURED (274 rows / 99 accepts / 55
gated / 99 iterated / 528 checks — old 144/45/66 was stale independent
of STD1b) and a second stale copy of the same figures fixed in the
earned-its-keep section. Worktree removed. Only std1-rearm (STD1c)
outstanding; merge chain to main after it lands + spec_mod0 re-verify.

### Seventeenth session, phase boundary 7 — STD1 merged to main, close battery running

std1-rearm landed (552efe2, reviewed: spec-faithful, five sabotage
evidences incl. the validating find that the old ENABLED_RE missed
PCREC_DEFAULT_FEATURES — the exact gap phase C existed to close; measured
gate.pairs classes 24 / modifiers 20, compared_pairs 44, eligible 22,
baseline 23, isolation 9 symbols / 4 TUs / 36 pairs). Merged into
std1-flip; manager fixed spec_mod0/CLAUDE.md's stale 13/1 summary +
check02 row (transient state, resolved same day). Final spec_mod0 gate
on composed branch: 14/14 exit 0.

std1-flip MERGED TO MAIN at db86a69 (journal conflict resolved
chronologically — flip branch carried boundaries 5/6/compliance, main
carried 3/4/composition; both kept, ordered). Plan substates STD1a/b/c
-> completed; [STD1] itself stays STATE:started until the close battery
is green. CLOSE BATTERY launched async (scratchpad/battery.log): the
ruled shape ending in bench-alone and mech (tree committed first — mech
archives HEAD).

State if interrupted here: main holds the complete STD1 landing at
db86a69 + these doc edits (uncommitted); battery result in
scratchpad/battery.log ("=== BATTERY COMPLETE ===" trailer; per-step
"BATTERY STEP: <name> (exit=N)" lines — every exit must be 0, mech
trailer must read 35 rows undetected:0 anomalies:0 pc3-skipped:0...
NOTE mech row count may have grown with STD1's new checks; judge against
the trailer's own undetected/anomalies zeros, not the old 35). On green:
[STD1] -> completed + archive row to plan_completed.md, journal close,
wake.md rewrite, push per Frank's standing end-of-session call.

### Seventeenth session close — [STD1] COMPLETED

CLOSE BATTERY GREEN at db86a69: make, strict, test LINTGEN=1, spec_mod0,
fuzz --seed 1, ubsan, asan, lint, bench (alone), mech — every step exit
0; mech trailer 35 rows (undetected: 0, anomalies: 0, pc3-skipped: 0).
The mech row count did NOT grow (STD1's new checks live inside existing
sections); judged against the trailer's zeros as planned.

Bookkeeping: [STD1] + STD1a/b/c archived to plan_completed.md (dated
group, landing record with all merge hashes and the new baseline);
plan.md's Next section now points at M4 (milestones start with Frank;
PC-5 + subst-template note before the match-API freeze, callout-ABI
alignment a design input to the same freeze). std1_check_rearm.md
retired (git history holds it; sabotage evidence in the STD1c merge
message). wake.md rewritten for session eighteen.

NEW BASELINE (supersedes 569b48f figures): corpus 1284, cli 247, reject
528 checks (274/99/55/99), codegen 34, registry 168, PC-3 163, spec_mod0
14/14 ARMED, trie 7, thread 8, mech 35. Bare default = std1 =
{classes, modifiers}; --features none = old bare behaviour verbatim;
library raw default still empty (D37 addendum).

Session lessons: (1) an expected-red integration branch (std1-flip) kept
main green through a 5-merge landing — the flip riding WITH its
re-baseline, not ahead of it, is the shape to repeat at std2. (2) Lanes
that go idle mid-async-run need artifact-based watchers on the manager
side (two lanes needed completion nudges; the watcher pattern worked
both times). (3) The check-rearm spec written BEFORE implementation held
without amendment — and its one prediction (the aperture gap) was
confirmed by the implementing lane's own nm discovery.

## 2026-08-14 — Eighteenth session: M4 pre-freeze package landed AND ruled (D38/D39); (?C flip

Frank opened with a general go ("start development, use parallel
development if there is an opportunity"). Three lanes ran the plan-named
pre-freeze work; every deliverable is merged, and Frank then ruled the
entire decision surface interactively in-session.

**Lanes (3, the cap; all worktree'd, all merged and cleaned up):**

1. pc5-options (sonnet): docs/pcre2_options.md — 80 flags/values, 10
   measured against libpcre2 10.46 with probe + transcript. Manager
   review resolved its three flagged caveats before merge (modifiers
   letter set verified J U a i m n r s x; ALT_VERBNAMES premise
   corrected — named backtracking-control verbs are the OUT-OF-SCOPE
   population, not verbs wholesale). Merged 258fd79.
2. m4-subst-note (strong model): docs/design/subst_template_design.md —
   C1-C11 capture-offset requirements ON M4's match API, module tiering
   subst/subst-extended/subst-pcrec, 12 pre-stated probe predictions
   with 3 refuted (unset-group err-55 default; global empty-match rule;
   C6 poison-cell agreement). Merged 3d5a9e8; its rx_ctx reconciliation
   amendment (adopting the callout ABI's pair type and returning the
   rx_span-break, ncap-watermark and unsigned-char findings to the
   freeze) merged same day.
3. callouts-flip (sonnet): [M4-CALLOUTS] step 1 — registry (?C1) row
   ROADMAP_NEVER -> PLANNED, pins moved failing-first in the same
   commit (evidence in 1ee1c12), compliance prose + SR-4 index in the
   same change, full suite green with EVERY count at the db86a69
   baseline. Merged 84e5956. Its find: the K14 prose<->column check's
   naive generalization to all-ROADMAP_NEVER rows is wrong — RS_REJECTED
   rows carry the same column value for D34's unrelated
   PCRE2-rejects-it-too pairing; re-scoped to RS_MODULE (the real K14
   population, now zero, column-derived, re-arms on the next instance).
   Caught by RUNNING the check, not inspection.

**Manager-side design:** docs/design/design_callout_abi.md drafted, then
rewritten twice as Frank ruled in-session (R-a..R-d): matcher entry and
callout callback share ONE signature; captures-so-far travel in rx_ctx;
syntax UNDECIDED (near-PCRE2 for callouts, embedded code maybe
\{ ... }); collision rule (reinterpreting spellings are module-gated).

**THE DECISION PASS (Frank, interactive):** D38 records ~25 rulings —
rx_callout_ref {fn,user} binding structs (per-binding state; TLS for
per-thread; rejected: global user, per-call user), unconditional
match-here export, match-or-fail with <-1 reserved and
__builtin_trap()-enforced (longjmp abort refuted on setjmp-entry cost +
volatile hazards), captures opaque v1 with declared-in-syntax export as
the v2 path, all fourteen subst questions (headliners: unset renders
EMPTY by default as a generation axis making python the clean oracle;
length-only no-NUL output; sizing exact-by-contract; rx_span BREAKS at
the M4 freeze to the ptrdiff_t pair — Frank: clearer under UTF), and
PC-5's disposition column ratified wholesale (3 rows individually).
D38 addenda: PCREC_* is the sole native flag namespace, PCRE2_* is
compat-only. D39 + addendum: every pattern exports a static
{name, number, ref} group index (born with the ref column so V-E
extends data not ABI); rx references use APPENDED numbering (primary
1..N stable); collisions resolved by caller-supplied labeled references
("a:reg1", nested paths "c:a"). Propagated into all carrying docs by
the d38-apply lane (merged 7fb6646); [PC-5] archived completed.

**State at this entry:** main at 84e5956 + this bookkeeping; smoke 6/6
green on the composed tree; all counts at baseline (corpus 1284, cli
247, reject 528, codegen 34, registry 168, PC-3 163, trie 7, thread 8,
mech unchanged — no mech run this session, close battery owed if the
session ends after more source work). Open on the design side: callout
syntax spelling (§6 Q5) and embedded-code restrictions (Q6) only.
NEXT: expand [M4.0] into substeps against the fully-ruled input set.

**Lessons:** (1) A live decision pass with the user beats asynchronous
ruling documents — ~25 rulings landed in one sitting because every
question arrived with its measured context and a recommendation. (2)
The K14 re-scoping is the check-design lesson again in a new costume:
two populations sharing a column value for different reasons will
false-positive any check that reads the column alone. (3) Two design
docs converging on one ABI (F3's one-representation rule) surfaced the
rx_span break BEFORE the freeze rather than after — the coupling rule
did its job. (4) Lanes idling mid-async-run happened twice more; the
artifact-watcher + nudge protocol recovered both without a wrong call.

### Eighteenth session close — [M4.0] expanded, dev deferred

Frank's closing rulings: start the M4.0 expansion, save actual dev work
for next session; the engine design gets its own doc in docs/design.
Answered honestly in-session: the M4 DESIGN DOES NOT EXIST YET and
nothing M4-shaped has been critiqued — today's ruled docs are inputs,
and both are unpaneled. The expansion (5b48537) is therefore
design-first and panel-gated: M4.1 match-API freeze doc
(docs/design/match_api_m4.md), M4.2 engine doc (docs/design/engine_m4.md),
M4.3 D6 panel over both PLUS the unpaneled design_callout_abi.md and
subst_template_design.md as a HARD GATE, then M4.4-M4.7 (announced API
break; VM emitter core + capture oracle + D27 author; selection/hybrid/
islands measured; capture differential + SR-8 flip + close battery).
Next session starts at M4.1/M4.2. Tree committed clean; smoke 6/6 green
post-flip-merge; wake.md rewritten; pushed to origin per standing call.

## 2026-08-14 — Nineteenth session: M4 design built, paneled, frozen; K17 found-and-fixed; implementation open

Frank opened with "begin dev when ready" against wake.md's queue (M4.1 +
M4.2). By close: BOTH design docs written and merged, the entire
remaining ruling surface closed interactively (D41–D44 + addenda, ~25
more rulings across four batches), the R21 panel run and every finding
dispositioned, a LIVE SHIPPED MISCOMPILE found by the panel and fixed
the same day, and the MATCH-API FREEZE DECLARED as the M4 working
baseline. [M4.1], [M4.2], [M4.3] all completed; [M4.4] is open.

**Lanes (six across the session, sequential ≤2 concurrent, all merged
and cleaned up):** m41-matchapi (sonnet; match_api_m4.md, merge
65b16c6); m42-engine (strong model; engine_m4.md, merge b726386 — DD-9
decided, SR-8's flip measured smaller than its row, three ABI tensions
reported not resolved); m4-amend (sonnet; D41–D43 integration + rx_info,
merge 96b8179); r21-fixes (sonnet; all D44 dispositions across four
docs, merge f2629a3); k17-fix (strong model, pre-tiering-rule; the K17
fix, merge of fb95b88/62690a9); plus three R21 critics (read-only).

**The ruling record (decisions.md):** D40 pre-v1/at-v1 versioning stance
(+ addendum: docs/spec is the contract vehicle; spec charter sharpened —
build history excluded, design references informational only). D41
fixed rx_* ABI type names, <prefix>_match, named-only group index,
match_caps entry ADDED, search posture (one-shot primitive; emitted
loops own dense iteration; <prefix>_iter the designated cursor
extension; find-all rejected as primitive) + [OPT-SIMD] row. D42
captures ON by default, RX_NCAPS artifact rule, reservation kept,
err-tag spelling + V-A alias obligation, caps lifetime, DD-2 two
bounds, DD-7 split ([ENG-ABS]), DD-9 archived to BENCH-1's worklist
head. D43 (+2 addenda) the rx_info reflection struct (Frank's own
direction: consistent CLI → PCREC_* bit → pcrec_options.flags funnel;
pattern embedded unconditionally; THREE counts after his
names-vs-groups catch; V-E direction: referenced patterns contribute
slots only for NAMED groups). D44 (+ working-baseline addendum) the
R21 dispositions: frame-ceiling design (cursor extension +
stamped residual ceiling), caps-array search signature at M4.4
(<prefix>_span RETIRES), slot column born into rx_group_entry, K17
fix-now, rx_info hardening (abi member, pattern_len, 64-bit flags,
ncaps = RX_NCAPS, ENGM engine int, int64 budget), --engine=dfa refusal,
--no-captures × $n --replace compile error, PCREC_CASELESS.

**R21 (docs/dev/reviews/2026-08-14-r21-m4-design.md):** 3 critics, 36
findings, 11 tier-1. Headlines: E-1 → K17, a live shipped DFA priority
miscompile ((?:b*?(?:a*)*)* on "ab": pcrec [0,2), BOTH oracles [0,1)),
found by executing the design's own P-1 probe; E-2, the design's
empty-guard wrong for bounded repeats (60/225,240 vs libpcre2; 0 with
guard iff rmax==-1); E-3, the Θ(n) frame/trail working set capping
capture matching at ~2 KB of subject under D19's thread-stack budget;
A-1, the span array-typedef's measured silent-stack-smash at the M4.5
signature change; A-2, the fixed ABI types failing to compile when two
differently-prefixed headers meet in one TU. ASK-1 REFUTED: python vs
PCRE2 disagreement measured ZERO across 225,240 pairs — the planned
oracle-exclusion mechanism would have HIDDEN K17; replaced by the
three-way 2-1-minority rule. All 11 STRUCTURAL citations held; what
broke was what was marked BELIEVED.

**K17 fixed same day** (the k17-fix lane): K1's one-shot redirect guard
in clo_visit removed — the empty-iteration rule is a property of the
ARRIVAL, with a termination argument replacing the guard. 120
oracle-verified family tests (corpus 1284→1404); 294/294 changed span
cells old-wrong→new-right over a 50,400-cell isolation sweep; 4477/4500
emitted-source blast radius byte-identical; sabotage-validated fuzz trap
templates (28 pre-fix divergences → 0; the class goes from ~1e-4 joint
probability to ~4% of generated patterns). Manager independently
re-verified the repro both sides. The fix's own validation sweep found
**K18** — the structurally distinct sibling (re-arrival THROUGH a seen ε
state; the memo is global, the rule is path-dependent) — opened,
ratcheted (165 known_fail cases + 7 controls), scheduled DESIGN-FIRST
before [M4.6], which does not open with it unfixed. The lane also caught
its own vacuous isolation check (a 0-changed control whose generator
couldn't produce the class) — two new check-design lessons recorded.

**Frank's session threads, all recorded:** the rx_ctx user-data
re-examination (kept, noted in the doc); the v1 stance (D40); the spec
charter; the pcrec_options funnel question that became D43/rx_info; the
two-counts catch (D43 addendum); the leftmost-first vs leftmost-longest
discussion that confirmed K17 is a bug under the ruled standard; the
frame-anatomy and alignment questions (recorded in engine §2.5 with the
SoA packing constraint); the fixed-stride cursor ladder (his z(ab)*y
question) and the REVERSE-DETERMINISTIC rung (his "play the regex
backwards" — five-rung ladder now in §2.5); the DD-8 tracer upgraded to
requested; --engine do-or-die confirmed with prefilter-off comparison
semantics; model tiering (sonnet default / opus difficult / manager
model never in lanes — CLAUDE.md + memory).

**State at close:** main pushed; [M4.1]–[M4.3] completed and archived;
freeze DECLARED (match_api_m4.md FROZEN as working baseline;
engine_m4.md DESIGN OF RECORD; weight per D44 addendum). Counts:
corpus 1404, cli 247, reject 528 (274/99/99/0), codegen 34, registry
168, PC-3 163, PC-4 62,872 cells 0 disagreements, trie 7, thread 8,
known_fail 1 (K18, deliberate). make test + strict green (k17-fix
battery); ubsan + asan both axes green on the composed tree; lint/
bench/mech owed at [M4.4]'s close. Open K-list: K2, K7, K9, K18.
NEXT: [M4.4] — the announced API break, per match_api_m4.md §11's
mechanical checklist.

**Lessons:** (1) A design panel on a genuinely load-bearing surface
found a shipped miscompile that 1284 tests and a span-comparing 1.24M-
pattern fuzzer missed — by executing the design's own named prediction;
budget critic probes by the BELIEVED marks. (2) The oracle-exclusion
inversion: the noise the mechanism guarded against measured zero and
the mechanism would have hidden the real bug — instruments point at
pcrec first. (3) Crossed lane messages caused three near-misses this
session (extension not landed, duplicate work, wrong-directory commit);
the verify-the-extension-landed grep and worktree-state checks caught
all three. (4) Frank's engineering questions (counts, alignment,
stride, reverse-scan) each improved the design and each took minutes to
record — the live-discussion channel is the project's cheapest
high-quality critic.

## 2026-08-14 — Twentieth session: [M4.4] the announced API break LANDED; full battery green; lint/bench/mech debt discharged

Frank opened with "begin dev when ready" against wake.md's queue ([M4.4]).
One writer lane (m44-apibreak, sonnet per the tiering rule, worktree off
4c26989) implemented match_api_m4.md §11's twelve-item checklist end to
end; the manager reviewed, added one fix, merged (c18e904), and ran the
FULL battery — every leg green.

**What landed (break commit 1dbb6ce, one announced break, no staged
migration):** `<prefix>_span`/`emit_span_typedef` RETIRED — `<prefix>_search`
takes `ptrdiff_t (*caps)[2]` directly (final shape), every _span site
updated including D44/A-7's three missed sites and --emit-main's %zu→%td;
the six fixed ABI types (rx_ctx, rx_matchfn, rx_callout_ref,
rx_group_entry, rx_info, rx_renderfn) emitted once per file under the
prefix-independent PCREC_RX_ABI_H guard; `<prefix>_match` +
`<prefix>_match_caps` retrofitted onto the DFA via search (leftmost-first
makes reported-start==pos exact anchored matching — no second automaton);
`<prefix>_info` in .rodata with all D44.5 fields (several
trivially-default pending M4.5/named-groups) and a NEW
emit_c_string_literal escaper (three-digit octal only — no \x gluing;
unconditional \? — trigraph warning found failing-first against
review_r21.rxt's `(b??(a*)*)*`); pcrec_error.input +
PCREC_ERR_INPUT_PATTERN; pcrec_options.flags uint64_t word
(PCREC_CASELESS D44.8 / PCREC_EMIT_MAIN / PCREC_NO_CAPTURES reserved);
RX_ERR_STEPS(-2)/RX_ERR_FRAMES(-3) reserved; +3 codegen checks (34→37).

**The lane's own miscompile-shaped find, needing a Frank ruling:**
`<prefix>_info` under the DEFAULT prefix is the literal identifier
`rx_info` — byte-identical to the ABI type's name — so §5's bare-typedef
spelling failed to compile on every default-prefix build ("redeclared as
different kind of symbol"). Landed as struct TAG only (tags are a
separate C namespace; every reference spells `struct rx_info`), the one
ABI type where the collision is reachable. Recorded as an as-built
deviation in match_api_m4.md §5; OPEN: bless struct-tag-only, or rename
the per-artifact instance and restore the typedef.

**Check movements (all traveling in the break commit, per the landing
bar):** OS-1's whole-file diffs and parse's ast-identity narrowed to the
rx_search ENGINE BODY — rx_info.pattern/flags differ BY DESIGN between
spelling-different-but-AST-equal patterns and across -i (the D37
stamp-differs shape); the codegen dup-typedef assertion INVERTED
deliberately (the guard's whole job is to make duplication a no-op) with
a new cross-prefix two-headers-one-TU compile as A-2's positive control;
S04 mech sabotage retargeted to guard-neutering (#ifndef → #if 1).
Manager review found ONE vacuousness hole in the lane's rescoping: parse's
rx_search_body() extraction returning empty on both sides counted as a
PASS — fixed (2498bf4) to hard-fail, matching codegen body()'s -s guard.
The codegen side already had a live non-vacuous control (negi≠negwrong).

**Battery (all at c18e904):** make test green — corpus 1404, cli 247,
reject 528 (274/99/99/0), parse 8, codegen 37, registry 168, PC-3 163,
PC-4 273 patterns/62,872 cells/0 disagreements, trie 7, thread 8,
known_fail 1 (K18 deliberate; ratchet silent). strict, ubsan (both
axes), asan (both axes), lint all green. bench green (floors held).
mech: 35 rows, 0 undetected, 0 anomalies — S04's retarget hit exactly
its documented 2-fail figure. THE LINT/BENCH/MECH DEBT OWED SINCE THE
EIGHTEENTH SESSION IS DISCHARGED.

**Process notes:** the lane went idle without its final report arriving
(a known pattern); the worktree-state check found the work complete and
committed — the commit-message-as-report house style meant nothing was
lost. Single-lane was the right call: M4.5 shares the same files and
K18's design note isn't needed until the M4.6 gate.

**State at close:** [M4.4] COMPLETED and archived; main pushed. NEXT:
[M4.5] — VM emitter core per engine_m4.md (cursor ladder, counter
mechanism, .rxt capture-expectation format + python span-oracle tier,
three-way differential rule, D27-blinded capture test author, DD-8
tracer scheduled with bring-up). [M4.6] still gated on K18 design-first.
Open Frank items: the struct-rx_info spelling ruling (above), callout
syntax Q5/Q6, V-E-time items.
