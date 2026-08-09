# pcrec Project Plan

Working plan derived from ../APPROACH.md. Milestones M0–M7 mirror APPROACH §9.

## Step-state format (grep'able)

Every step line matches exactly:

    - [Mx.y] STATE:<state> — <title>

States: `not-started` | `started` | `completed` | `blocked` | `deferred`

Find work:

    grep -n "STATE:started" docs/plan.md
    grep -n "STATE:not-started" docs/plan.md
    grep -c "STATE:completed" docs/plan.md

Rules: update the STATE tag in place when a step changes state; expand a milestone
into substeps only when work on it begins (replace its single `[Mx.0]` line);
note blockers inline after the title with `(blocked: reason)`.

## M0 — Scaffold & process

- [M0.1] STATE:completed — directory layout, GNU Makefile
- [M0.2] STATE:completed — docs: plan.md, dev_journal.md, decisions.md
- [M0.3] STATE:completed — CLAUDE.md in each directory
- [M0.4] STATE:completed — test harness: run.sh, driver.c, docs/testing.md (subagent)
- [M0.5] STATE:completed — base test corpus in tests/base/, python-re cross-verified (subagent)

## M1 — Base compiler end-to-end (ASCII, string source, DFA engine)

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

## M2 — Optimizer & long-text performance (seeded by R1 findings)

- [M2.0] STATE:completed — DESIGN GATE (R1 A-2/A-3): adopt the search-from-anywhere self-loop automaton (kills O(n²), same shape M3 streaming needs) and the hybrid emitter (computed goto for small DFAs, table-driven for large); re-ground the state cap in measured gcc compile time
- [M2.1] STATE:completed — scan-avoidance: memchr/bitmap start prefilter, self-loop skip states (fwd+rev), anchored fast path (^-only patterns skip the start loop)
- [M2.2] STATE:completed — DFA minimization (Moore signature refinement, EOL-view as extra symbol); alternation-to-trie DEFERRED with rationale: subset construction already merges alternation prefixes in the final DFA, so a trie pass would only shrink the intermediate NFA (compile-speed win with no current budget pressure)
- [M2.3] STATE:completed — tests/bench: throughput budgets AND gcc-compile-time budgets on generated code as regression tests (R1 A-3)
- [M2.4] STATE:completed — coverage breadth (R1 P-M1/P-M2/P-N1/P-N2): CLI surface, library API direct, startpos != 0, long subjects, high bytes/NUL
- [M2.5] STATE:completed — PCRE2-oracle differential fuzzer committed to tests/ (pulled forward from M7; R1 lesson — semantics critic's libpcre2 binding)
- [M2.6] STATE:completed — K1 fix (landed early at R2: loop-entry empty-iteration rule; also fixed R2-S1 in BOTH engines)
- [M2.7] STATE:completed — engine unification for `$` (D8; `^` deferred, needs a reverse BOT variant) — engine unification (R2-A2, FATAL): `$`-without-`^` patterns route to ENG_ATTEMPT which has NO scan-avoidance and is still O(n²) — measured 14.3x slower on a log pattern, quadratic on `a*b$`. Either fold `^`/`$` into ENG_UNANCH (EOL-variant switching in fwd+rev, BOT handling in reverse) or give ENG_ATTEMPT prefilters. R1's A-2 is only half-fixed until this lands
- [M2.8] STATE:completed — NFA-level alternation trie (R2-A4, D9/D10): priority-preserving prefix trie in src/ir/nfa.c; the quadratic turned out to be closure FAN-OUT, not state count (measured 4045 visits/closure at 2000 branches, 2.36e9 total). 3600-word list: hard-fail -> 0.93 s. NFA cap re-derived 20000 -> 131072 so the emitter-grounded DFA caps bind first; clo_visit tail edges made iterative so the cap no longer depends on gcc's TCO. ALSO fixed an unrelated repo-fatal bug found on the way: `.gitignore`'s unanchored `core` had excluded src/core/ from every commit
- [M2.9] STATE:not-started — benchmark rigor (R2-B3/B4): taskset/chrt pinning + governor capture, repeat trials with variance reporting, engine-order interleaving, tighten budgets (currently 9x-300,000x loose; none would catch a 2x regression), fix case (c)'s early-exit budget and the sub-millisecond linearity check
- [M2.10] STATE:not-started — dense/counting-pattern codegen (R2-A5): case (f) is bound by the serial load-to-load dependency chain (NOT cache footprint, NOT branch prediction — both ruled out by measurement); no skip-eligible states. Also build the computed-goto-vs-table arbitration D7 promised and M2.3 never delivered (docs/known_issues.md): empty-iteration handling so zero-width $ keeps priority in quantified groups (scheduled with M6 assertions)
- [M2.11] STATE:not-started — process ratchets (R2-PR7/PR8): a pass/fail gate for tests/bench/compare so headline performance can't silently regress; an automatic check that flags a tests/known_fail case which starts PASSING (a bug fixed by accident should not sit unnoticed)
- [M2.12] STATE:completed — restore prefilter/skip loops on the EOL engine path. The two emitters M2.7 forked are merged back into one EOL-aware emit_unanchored (the fork IS how the `$` path lost these for a milestone); skips bounded at n-1, memchr keeps no early return, reverse skip carries a pp+1<n entry guard. Also required moving the accept/EOL evaluation AFTER the skips — bounding alone is not enough, a skip landing on n-1 would consume that byte before its EOL view was taken. `$` throughput 291 -> 22248 MB/s median of 7 (~76x), now at parity with the same pattern without `$`; non-`$` codegen byte-identical on 8 probe patterns

## M3 — Streaming input

- [M3.0] STATE:not-started — DESIGN GATE FIRST (R2-A3): D7's "same shape streaming needs" holds only for match-END finding. The reverse pass rescans backward through raw bytes a stream may no longer hold (unbounded for `.*` shapes). Design match-START finding under bounded memory BEFORE writing streaming code; reconcile with APPROACH §6's PARTIAL/WINDOW_EXCEEDED contract
- [M3.1] STATE:not-started — *_stream_* API for the DFA engine, chunk-boundary tests

## M4 — Captures + backtracking VM engine

- [M4.0] STATE:not-started — milestone (expand on arrival): VM emitter, DFA-prefilter hybrid, DFA islands

## M5 — UTF-8

- [M5.0] STATE:not-started — milestone (expand on arrival): byte-wise UTF-8 automata, \p{...} module

## M6 — PCRE feature modules

- [M6.0] STATE:not-started — milestone (expand on arrival): classes+ (\d \w \s, POSIX classes), assertions (\b \A \z, mid-pattern $), modifiers, lookaround, backrefs, atomic groups

## M7 — Hardening

- [M7.0] STATE:not-started — milestone (expand on arrival): differential fuzzing vs libpcre2, freestanding/embedded build profile, PCRE2 testdata import

## Checkpoint review gates (D6)

Every milestone ends with an adversarial critic-panel review of the work since
the last checkpoint; compiled results live in docs/reviews/.

- [R1] STATE:completed — M0+M1 checkpoint review (4 critics) — compiled + triaged in docs/reviews/2026-08-09-m1.md
- [R2] STATE:completed — M2 checkpoint review (5 critics; 4 reported, process/tests/docs critic did not deliver — lens carried to R3) — docs/reviews/2026-08-09-m2.md
- [R1.1] STATE:completed — all fix-now items applied and verified (2 wrong-answer bugs via EOL-variant states, 3 crash classes, leak class, LLP64 span type, PCRE accept/reject parity, harness integrity, CLI --); suite 353/353

## Design-debt ledger (from R1; resolve before the milestone that hits each)

- [DD-1] STATE:not-started — case-insensitivity design incl. Unicode folding vs byte-wise automata (before M5) (R1 A-7)
- [DD-2] STATE:not-started — VM engine match/step limits — ReDoS stance (with M4 design) (R1 A-8)
- [DD-3] STATE:not-started — generated-API versioning/compat policy for vendored consumers (before M3) (R1 A-10)
- [DD-4] STATE:not-started — \G / global-iteration semantics vs startpos (with M6) (R1 A-11)
- [DD-5] STATE:not-started — --std-c portable emitter fallback (switch-based) (R1 R-5)
- [DD-7] STATE:not-started — engine unification ownership (R2-A6): D7 promises ENG_UNANCH eventually absorbs `^`/`$` but no milestone owns it; M4 must also decide WHICH machine becomes the capture prefilter now that the engines forked; DD-4 (\G) must note `nfa_wrap_unanchored` bakes in the self-loop with no toggle
- [DD-8] STATE:not-started — `--emit-ir` / `--emit-dot` promised in APPROACH §6, never built (R2-A7)
- [DD-6] STATE:not-started — multiline ^/$ as DFA state context — interacts with state budget (with assertions module) (R1 A-6)
