# tests/base — base-tier regex test corpus

Comprehensive test suite for base-tier PCRE features: literals, character classes, quantifiers, alternation, anchors, groups, and basic escapes. Every expectation is cross-verified against python3 re to ensure semantics match PCRE for this tier.

## Files

- **literals.rxt** — literal character and substring matching
- **dot.rxt** — dot (.) matching (any byte)
- **classes.rxt** — character class [...] syntax and behavior
- **class_brackets.rxt** — the MEMBER SETS of the class-bracket patterns FIX-2
  changed the verdict of (`[a[:b]`, `[[:alpha]`, `[.a]x.]`, `[a[.b]c]d.]`, the
  K4 rule-3 discriminators, both doorway-4a controls). They were guarded only by
  `accept` rows asserting exit 0 and a non-empty file — "did not say no" — and
  appeared nowhere in this corpus, so R9/C1-F4's one-line sabotage that DROPS
  the `:` from `[a[:b]`'s member set passed every suite in the repo and the
  differential fuzzer. Sabotage-validated: that edit fails 4 cases here
- **quantifiers.rxt** — *, +, ? quantifiers
- **bounded_repeats.rxt** — {m,n} repeat syntax
- **d27_forms.rxt / d27_bodies.rxt / d27_nesting.rxt / d27_edge.rxt /
  d27_captures.rxt / d27_large_counts.rxt** — the D27 blinded quantifier /
  bounded-repeat corpus (2026-08-16, cell `brepspec`): 81 blocks / 679 live
  case-lines written from the PCRE promise by an author denied `src/` and
  `tests/`, every expectation computed from python `re` and independently
  re-verified by a from-scratch checker. Covers every repeat spelling
  greedy+lazy, class/alternation/group/multi-char bodies, 2-3-level nesting
  with mixed preference, nullable-body edges, last-iteration-wins captures
  (incl. the branch-not-reset rule), 500-2000 counts and the 64-copy
  replication-cap boundary (`perr`). Two case-lines from the corpus live in
  `tests/known_fail/d27_nested_min_boundary.rxt` (K23) instead of here.
- **d27_k23_ambiguous_decomposition.rxt** — the D27 blinded corpus for the
  K23 ambiguous-decomposition region (2026-08-17, cell `d27k23`): 3 pattern
  blocks (`(a{1,3}){64,65,66}`) / 89 case-lines covering the 65..100 dense
  region, the 3N span cap, broken-run and offset-start composites. The
  region's python `re` oracle does not terminate, so expectations derive
  from a stated law (leftmost run of length L>=N matches [start,
  start+min(L,3N))) proven by exhaustive small-N induction and re-verified
  independently at review; verification ledger in
  docs/design/k23_impl/d27_corpus_notes.md. Lands WITH the [M4.6d] MRL fix.
- **alternation.rxt** — | alternation and precedence
- **alternation_trie.rxt** — priority hazards of M2.8 prefix-trie factoring (D9): shorter-branch-first shapes, overlapping-but-distinct classes, mixed eligible/ineligible runs. Each guard is sabotage-validated — disabling the disjointness guard fails 2 cases, disabling index-range partitioning fails 7
- **anchors.rxt** — ^ and $ anchors
- **eol_engine.rxt** — M2.7 regressions: `$` patterns on the O(n) unanchored engine
- **eol_scan_avoidance.rxt** — M2.12 regressions: prefilter/skip loops restored on the `$` path (D11). Full entry in NOTES.md.
- **groups.rxt** — (...) capturing and (?:...) non-capturing groups
- **xbrace_space.rxt** — spaces and tabs around the digits of `\x{...}`
  (K117, lane langfix): accepted before and after, refused among them, no
  effect on the range check or the digits-missing rule. Every block
  `# pcre2-only` (python has no braced `\x`), libpcre2 10.46
- **escapes.rxt** — \\ \" \n \t metachar and control escapes
- **empty_matches.rxt** — patterns matching empty strings
- **precedence.rxt** — operator precedence and grouping
- **leftmost_semantics.rxt** — leftmost-first match semantics (greedy/lazy precedence)
- **review_r21.rxt** — K17's regressions (R21 finding E-1, fixed 2026-08-14). Full entry in NOTES.md.
- **k18_empty_exit_through_seen_eps.rxt, k18_arm_order.rxt, k18_split_shapes.rxt, k18_deep_nesting.rxt, k18_cost_gates.rxt** — the K18 regression corpora (docs/dev/known_issues.md K18); read them together, none alone is the acceptance criterion. Per-file entries in NOTES.md.
- **syntax_errors.rxt** — malformed patterns and diagnostic accuracy, including the K5/K6 brace miscompiles fixed 2026-08-10 (FIX-1). Full entry in NOTES.md.
- **comment_escape.rxt** — pcrec-bench O-31 finding F1's regression net: a
  pattern whose own bytes contain a comment-closing STAR THEN SLASH (the same
  shape as the bench's WAF witness, `/*!*/` SQL-comment obfuscation), which
  used to corrupt the DFA emitter's per-state "shortest input" legend and
  fail to compile — see `src/gen/emit_dfa.c`'s `emit_comment_safe_byte` and
  `tests/codegen/run_comment_escape.sh`'s structural check for the mechanism.
  Two blocks, both oracle-verified against python3 `re`
- **k64_precheck_forced_vm.rxt** — [K64]'s regression (2026-09-25, lane
  k64fix): `email-nested-plus`'s pattern under `engine vm` with `budget
  steps=10000`, whose framed one attempt backtracks exponentially over a
  class run with no `@`. The four `n` cells gave up (`steps`, a hard failure)
  on 6ef76820-behaviour and answer NOMATCH once G2 keeps the pre-check; the
  `gu steps` cell is the control that the budget reaches the VM, and block 2
  is the frameless control G2 still declines on. Oracle-verified against
  python3 `re` (class runs of 16..20 bytes keep python's own backtracking
  fast); sabotage S274 is its failing direction
- **k65_precheck_whole_set.rxt** — [K65]'s regression (2026-09-25, lane
  k65fix): `(x?)([a-z]+)+Z.@\1` (backreference, so no hybrid: an unguarded
  framed VM program) under `encoding byte` and `encoding utf8`, whose picks
  differ (`Z` / `@`), plus the run form `...Z.@#\1`, each with `budget
  steps=10000`. The `n` cells lacking the member the pick did NOT test gave
  up (`steps`) before the pre-check tested the whole necessary set — 9 of 24
  cells at 5a2094e7, 24/24 after; the `gu steps` cells prove the budget
  reaches the VM. Oracle-verified against python3 `re` (PASS=21, 3 gu
  skipped; runs of 16..18 bytes) and spot-checked on libpcre2 10.48;
  sabotage S277 is its failing direction
- **k66_precheck_whole_run.rxt** — [K66]'s regression (2026-09-25, lane
  k66fix): `(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` (backreference, so an unguarded
  framed VM program) under `encoding byte` and `encoding utf8`, whose
  8-byte windows of the 16-byte necessary run differ (`~#~#~#~#` /
  `eeeeeeee`), each with `budget steps=10000`. The `n` cells hold a window
  (and every set byte, so K65's half cannot cover) but not the whole run;
  they gave up (`steps`) before the pre-check compared the whole run — 8 of
  16 cells at the k65fix base `bbbf58e5`, 16/16 after. A 16-byte `!` tail
  keeps the VM's minimum-remaining-length prune from hiding the backtracking
  at these lengths. Oracle-verified against python3 `re` (PASS=14, 2 gu
  skipped) and spot-checked on libpcre2 10.48; sabotage S278 is its failing
  direction
- **possess_lazy_guard.rxt** — the 20 D47.6 lazy-possessification guard cells (docs/dev/decisions.md D47 ruling 6). Full entry in NOTES.md.
- **nullable_anch.rxt** — [NULLABLE-ANCH] (lane nullanch1, 2026-10-08): the
  five movers of the anchor-aware nullability decline (bench
  `evil-alt-nested`/`trim-nested-star`, corpus `^(a{2,4})?$`,
  `^(a?)(?1)*$`, `^(?:(?<g>a?)){0}(?&g)*+$`), every cell libpcre2 10.46's
  answer written by `docs/dev/optloop/nullanch/pcre2_cells.py --rxt`. Two
  GIVE-UP CELLS (17 letters + `!`, 32 blanks + `x`) are the answer-level
  detector: before the row the default VM exhausted its step budget there
  (sabotage S612). They are `# pcre2-only` for python's cost and libpcre2's
  match limit (U19, U4); their `nomatch` is verified on the language-equal
  patterns and by python offline (the transcript).
- **vm_lazy_rmin_prefix.rxt** — [MEMFN] R-12 (lane vmlazy, 2026-10-09): the
  VM cursor rung's LAZY rmin prefix, a span scan capped at rmin plus the
  rung's reach test. Runs short of rmin at stride 1 and 2, exactly rmin,
  past rmin and rmin = 200, each pattern on the default route and under
  `engine vm` (the only route where the prefix alone must refuse a short
  run). Generated from python3 `re`; sabotage rows S706-S708/S710's
  detector.
- **opt41_rung_nullable_decline.rxt** — the [OPT-4.1] `--emit-ir` prefilter
  value `no-nullable-collapsed` REACHABILITY WITNESS (adm71 item 4,
  2026-09-19): `docs/dev/lanes/dd8_report.md` section 4.3 filed that value
  UNREACHED BY ANY INPUT; a captures-free, nullable, collapsible-repeat
  pattern whose DFA-as-ENGINE build overflows `PCREC_MAX_DFA_STATES_TABLE`
  under `auto` refutes it — the [SEL-1] collapse rung IS offered and IS
  declined for nullability, `RX_ENGINE_SEL "declined-nullable"`. One block,
  `(?:ab){0,16000}` (the smallest round N found past the 32,000-state
  boundary), six oracle-verified cases against python3 `re`

- **clspack_atoms.rxt** + **gen_clspack_atoms.py** — [OPT-CLSPACK]'s answer
  corpus (2026-09-30, lane clspack; `docs/spec/tuning.md` §2.34): VM byte
  classes that read a table and SHARE ONE ATOM TABLE. The shipped corpus has
  no artifact the atom row fires on (the most per-site bitmaps any corpus
  artifact carries is 6), so every block is a constructed witness, GENERATED
  by the script beside it with every expectation python3 `re`: eleven
  scattered classes (the threshold, exactly), ten (one short), twelve read
  from a span-loop cursor/lazy loop/counted repeat/`\b`, and two crafted
  eleven-class blocks over 63 and 64 bytes with distinct membership codes
  (64 atoms fires, 65 declines; `engine vm`, their default route is the
  DFA). 79 cells. `tests/codegen/run_clspack.sh` reads the same blocks by
  case name and asserts which took the atom table; sabotage S400/S403 are
  this file's failing directions

## Conventions

Format: `pattern <regex>` followed by `m "<subject>" START END` (match expected) or `n "<subject>"` (no match). Escapes in subjects (\" \\ \n etc) are encoded as literal backslash sequences for shell safety; driver.c decodes them. Run via `make test` or `bash tests/harness/run.sh tests/base/`.

Maintenance: update this file when .rxt files are added/removed or feature coverage changes.

See also NOTES.md in this directory (history, lessons, rationale, moved detail).
