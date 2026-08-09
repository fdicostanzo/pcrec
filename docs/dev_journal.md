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
