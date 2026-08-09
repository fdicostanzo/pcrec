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
