# w2census_report.md — [REVW.2] emit_dfa.c third-category census + listing-reach measurement (2026-09-18, lane w2census, sonnet)

Task: the two independent deliverables named in the brief — TASK 1, the
`[REVW.2]` row's stated precondition ("emit_dfa.c third-category census
FIRST"); TASK 2, the listing-reach measurement (input to a manager decision,
`tests/codegen/run_ir_listing.sh` deliberately NOT touched). Branch
`lane/w2census`, worktree `worktrees/w2census`, off `main` at `f6474777`.
Nothing under `src/`/`cli/`/`lib/` touched.

## TASK 1 — full findings: `docs/dev/w2census.md`

New script `tools/review/fragment_census.py` (python3 stdlib only): finds
every `char <ident>[<expr>]` declaration statement/declarator over named
files, classifies each declarator (a) bare integer literal, (b) bare
`PCREC_MAX_EMIT_NAME_LEN`, (c) anything else, using `reviewlib`'s existing
lexical mask so text inside emitted-code string literals is never mistaken
for a real declaration.

**Headline numbers:**

- `src/gen/emit_vm.c`: **58 statements / 67 declarators** (a: 46, b: 16,
  c: 5). This is ONE declarator more than EP2's reported 66 — the script
  disagrees, not the tree: the extra declarator is `flr[32]` at (current)
  line 4894, `vm_revdet_rep`, sharing a 3-declarator statement with two
  `PCREC_MAX_EMIT_NAME_LEN` buffers (`rv`, `cur`). EP2's own line/statement-
  oriented tally folded the whole statement into category (b) and dropped
  `flr` — a real, live scratch buffer — from its count entirely. Full trace
  in `w2census.md` §2.
- `src/gen/emit_dfa.c` (the population EP2 never measured): **23 statements
  / 25 declarators** (a: 9, b: 10, c: 6). Category (c)'s six sites are
  tabled in full in `w2census.md` §3, including a cross-file observation:
  `PCREC_STARTPOS_GUARD_TEXT_MAX` (a bare OTHER governing-limit macro, no
  margin) sizes THREE sites total across both files — `emit_vm.c`'s
  `mguard` (EP2's own find) plus two in `emit_dfa.c`.
- **Combined floor for the repaired criterion** (ANY size expression,
  excluding only `Vm.up` by name per lens 10's own scope note): raw combined
  81 statements / 92 declarators; less `Vm.up` (`emit_vm.c:376`, category a,
  the one struct field lens 10 scopes out of wave 1 entirely) = **80
  declaration statements / 91 declarators.**

## TASK 2 — the listing-reach measurement

**Method.** Rebuilt w1stage0's `listing_reach_census.py` in the session
scratchpad (never committed — it is instrumentation, not a deliverable) and
confirmed it reproduces w1stage0's own numbers exactly at this branch point:
27/41 `vm_rolef` sites for the 11-pattern fixture, 31/41 for the whole
corpus at default engine selection. No drift since w1stage0.

**Root cause of the missing families, found before searching for
patterns.** Neither `run_ir_listing.sh`'s own invocation
(`pcrec_run "$PCREC" -p rx --engine=vm --emit-ir -- "$pat"`) nor
`listing_reach_census.py`'s corpus arm ever passes `--features`. Three of
the four entirely-missing families are **module-gated** constructs
(`lookaround`, `recursion`, `atomic-groups`) that refuse to compile at all
without the matching `--features` flag — so their 0/N reach in BOTH
populations is not evidence the corpus lacks the right shapes (it doesn't;
`tests/lookaround/`, `tests/recursion/`, `tests/atomic_groups/` all have
them), it is evidence the harness never enables the module that would let
any pattern reach them. This is a real, previously-unstated fact about the
instrument, not only about the corpus.

**Minimal added set — five patterns, ALL already in the corpus (none
hand-written), each with the `--features` its module requires:**

| pattern | source | features | sites it adds |
|---|---|---|---|
| `(?<=a\|bc)x` | `tests/lookaround/lookbehind_widths.rxt` | `lookaround` | `vm_look_behind` ×4 (`:6369,:6399,:6409,:6441`) |
| `^(?:(a{2,5}(?1)?b)((?1)c)){0}(?2)$` | `tests/recursion/bothlinkage.rxt` | `recursion` | `vm_call` (`:6862`), `vm_splice` (`:7006`), `vm_region` (`:7138`), `vm_opt_chain` (`:4449`, incidental) |
| `^(a)\1$` | `tests/backrefs/gated.rxt` | `backrefs` | `vm_emit`'s `"backreference to"` site (`:7571`) |
| `((a)\|ab){0,12}?c` | `tests/counterk/counterk.rxt` | (none — base grammar) | `vm_opt_chain` (`:4449`), `vm_counter_rep` ×2 (`:5543,:5547`) |
| `(?:a\|ab){2,3}+` | `tests/atomic_groups/possessive.rxt` | `atomic-groups` | `vm_poss_chain` (`:4547`), `vm_opt_chain` (`:4449`, incidental) |

**Measured reach with the fixture + this set: 39 of 41 (up from 27 of
41).** Every candidate's own contribution was measured individually (a
per-pattern diff against the fixture-alone unreached set), confirming no
double-counting beyond the incidental `vm_opt_chain` overlap noted above.

**Two sites remain unreachable by ANY pattern, and the reason is
structural, not a population gap:** `vm_counter_phase`'s two call sites
(`emit_vm.c:5317,5351`) format their whole role text as pure arithmetic
(`"%lld * ((ptrdiff_t) %d - slot_values[%d])"`) with **no literal prefix
before the first `%` conversion** — `literal_prefix()` returns the empty
string, and the census's own hit test (`bool(prefix) and (prefix in blob)`)
is false by construction whenever the prefix is empty. w1stage0 already
named this as instrument-blind; this lane confirms no pattern changes it,
because the instrument itself cannot see this shape regardless of what
compiles.

**What the manager is ruling on.** Widening `run_ir_listing.sh`'s own
11-pattern `PATTERNS` array to include these five (or a subset) is a
stage-3-scoped decision this lane does not make — per the brief, the
script itself was not touched. Doing so would require BOTH the pattern
text AND a per-pattern `--features` flag the harness invocation does not
carry today, which is itself a small harness change (adding `--features`
support to that one invocation site), not just an array edit. If that
change is made, the measured reach is 39/41; the remaining 2/41 need a
different instrument (one that can name a call site by something other
than its own literal text) rather than a different population.

## Deliverables

1. `tools/review/fragment_census.py` (new) + `tools/review/CLAUDE.md`,
   `tools/CLAUDE.md` rows.
2. `docs/dev/w2census.md` — TASK 1's full method, population, per-site
   category-(c) table for `emit_dfa.c`, combined floor, instrument
   limitations.
3. This report (TASK 2's full findings; TASK 1 points at deliverable 2).

## Validation

- `make -j4 CC=gcc-16` (worktree build): clean.
- `python3 tools/review/fragment_census.py src/gen/emit_vm.c
  src/gen/emit_dfa.c`: runs clean; every multi-declarator statement it
  reports was independently read against the source with `sed -n` and
  confirmed real (including the two scoped `pf_emit_ofs_bounded` blocks in
  `emit_dfa.c` — two statements in two `if`/`else if` arms, not one
  double-counted).
- The listing-reach instrument was cross-checked against w1stage0's own
  committed numbers before any new pattern was tried (27/41, 31/41 —
  exact reproduction, confirming no drift since w1stage0 at this branch
  point).
- Each of the five candidate patterns' own contribution to reach was
  measured individually, not just as part of the combined set.
- No `src`/`cli`/`lib`/`tests` file touched; not an `abi` event. Only
  `make -j4` was run on this box per the brief's box note (no heavier
  suite).

## Rulings received

None — no ruling was requested or issued during this lane's run.
