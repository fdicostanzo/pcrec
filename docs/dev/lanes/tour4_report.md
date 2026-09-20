# lane tour4 — [TOUR-4] DFA_INVARIANT abort -> pcrec_ctx_fail (K61) + [ORG-7] nine no-reader exports

Branch `lane/tour4`, worktree `worktrees/tour4`, branch point `82dd396a`
(main was at `6bc0a5bf` when the worktree was created — same tree; the
CODE branch point named in the brief is `82dd396a`). Model: sonnet.

## TASK A — [TOUR-4] (design record: `docs/dev/reviews/2026-09-20-frank-tour.md`
section [TOUR-4]; finding: `docs/dev/reviews/2026-09-20-r61-fable-personal-review.md`
F1)

### What changed, per site

`DFA_INVARIANT(cond)` in `src/ir/dfa.c` was
`#define DFA_INVARIANT(cond) do { if (!(cond)) abort(); } while (0)`.
Three sites at `82dd396a` (the brief said two from memory; a grep found
three, matching the tour item's own correction):

1. `clo_open` (`src/ir/dfa.c:605` post-fix) — "loop not already open":
   `lctx_find(cl->ctxs, ctx, s) < 0`.
2. `clo_walk` (`:684` post-fix) — "the open loop is the walk's context
   stack top": `at == ctx`.
3. `closure()` (`:874` post-fix) — "the seen/emit stamp generations
   stayed in lockstep": `sc->seen.gen == sc->emit.gen`.

The macro is now:

```c
#define DFA_INVARIANT(cx, cond, msg) \
    do { if (!(cond)) pcrec_ctx_fail((cx), 0, "internal error: %s", (msg)); } while (0)
```

Each call site passes its own invariant's text as `msg`, matching the
comment already at each site (no new wording invented — the messages
paraphrase what the surrounding block-level comment already says the
check verifies).

`cx` reaches all three sites through a new `Ctx *cx` field on both `Clo`
and `CloScratch` (`src/ir/dfa.c`), populated exactly once:
`pcrec_build_dfa` (which already takes `Ctx *cx` as its first parameter)
sets `sc.cx = cx` right after `memset(&sc, 0, sizeof sc)`; `closure()`
reads `sc->cx` for its own site (before `Clo cl` exists yet) and threads
it into the `Clo cl = { sc->cx, ... }` initializer so `clo_open`/
`clo_walk` read it off `cl->cx`. No new parameter was added to any
function signature other than the macro itself — `pcrec_ctx_fail` never
returns (it `longjmp`s to `compile_driver`'s one recovery point), so the
three call sites need no post-macro control-flow change.

The macro's comment is rewritten: it no longer cites "this file's
existing idiom (tab_grow, intern)" (stale since K7 moved those two to
`pcrec_ctx_nomem`/`pcrec_ctx_fail` already) and instead explains the K61 fix
and cites `docs/spec/match_api.md` §8.1's caller-survives promise.

`src/ir/CLAUDE.md`'s `clo_walk` entry ("both of the design's invariants
ship as live `DFA_INVARIANT` aborts") was also stale after the fix and is
corrected to say `pcrec_ctx_fail` refusal, not `abort()`.

### K61 (docs/dev/known_issues.md)

Filed at the top of the file (newest-first, matching K60's placement),
status FIXED, citing the three sites, the fix shape, and sabotage S262
as the regression guard. See the entry itself for full text.

### Spec (docs/spec/match_api.md) — headline sentence unchanged, follow-on sentence corrected per manager ruling

Per the brief: "The spec is UNCHANGED (the fix makes it true) — confirm
by reading the sentence, and do not reword it." Read `:3345`'s headline
sentence ("It never `abort()`s the caller on the compile path.") — true
after the fix, left BYTE-IDENTICAL.

**Flagged mid-lane, then ruled on by the manager**: the very next
sentence in that same bullet ("Two `abort()`s remain in the code
deliberately... a 'cannot happen' DFA structural invariant, and the
syntax-dump path's detached string buffers") was factually stale after
this fix — only ONE `abort()` remains (syntax-dump's detached buffers).
Manager's ruling (relayed mid-validation): update it (D80 — the spec
travels with the change; "do not reword" was never meant to protect a
sentence the fix makes false), keep the headline sentence
byte-identical, touch nothing else in the file. Done: the sentence now
reads "One `abort()` remains in the code deliberately, and it is not on
the compile path: the syntax-dump path's detached string buffers... The
DFA structural invariants that used to be the OTHER exception now
refuse through `pcrec_ctx_fail` like every other 'cannot happen' site in
the compiler (K61, `docs/dev/known_issues.md`)."

### Sabotage S262

`tests/mech/sabotages/S262_dfa_invariant_loop_open_inverted.sh`. Before
writing it: **the brief's assumed highest S-id on main, S199, was wrong**
— `git ls-tree -r main -- tests/mech/sabotages/` shows the highest is
`S261` (269 files total), so the new row is `S262`, not `S200`.

Inverts `clo_open`'s condition (`lctx_find(...) < 0` becomes `>= 0`), so
the invariant fires on the FIRST loop essentially any DFA build opens
(any pattern with a repeated non-trivial subpattern), rather than only
on a genuine open-loop-context conflict. `SAB_SUITES="harness"` — the
arm that runs `tests/harness/run.sh` over the full `.rxt` corpus and
scores as `corpus:Nfail/Mpass`.

**DETECTED.** `bash tests/mech/run_sabotage_matrix.sh S262`:

```
S262-dfa-invariant-loop-open-inverted  src/ir/dfa.c  ...  harness  corpus:6190fail/22754pass  DETECTED

== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) at 0b685df2b9b97d3b7b5da12e75a51e0c5f2378c8 ==
```

6,190 of the corpus's cases fail under the plant (a large, ordinary
population — as predicted, since the sabotage fires on any pattern
opening a loop), 22,754 still pass, and the run completed to its
trailer with the standard verdict counts (0 unexpected/undetected/
unreached/anomalies) — no crash, no early termination, no SIGABRT: the
thing K61 exists to guarantee. Log:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/8f62ea75-43d2-4b00-8caf-d9b51bf26c8b/scratchpad/tour4_mech_s262.log`.

## TASK B — [ORG-7] (design record: `docs/dev/reviews/2026-09-20-code-org.md`
section [ORG-7])

Verified each of the nine named exports by `grep -rn '\b<sym>\b' src cli
lib tests tools` with no directory restriction, then a repo-wide grep
with no `--include` filter as a second check. Table:

| symbol | file | callers outside own file? | disposition |
|---|---|---|---|
| `pcrec_tune_row` | `src/core/tune.c` | none | `static`, decl removed from `internal.h` |
| `pcrec_bufsurface_inert` | `src/gen/emit_dfa.c` | none | `static`, decl removed |
| `pcrec_dfa_axis_cands` | `src/gen/emit_dfa.c` | none (never declared in `internal.h` either) | `static` |
| `pcrec_emit_abi_types` | `src/gen/emit_dfa.c` | **none anywhere, including its own file** | **left exported — dead, not touched** |
| `pcrec_nfa_has_asserts` | `src/ir/nfa.c` | **none anywhere, including its own file** | **left exported — dead, not touched** |
| `pcrec_registry_verb_name_limit` | `src/parse/mod_verbs.c` | none | `static`, decl removed |
| `pcrec_rxt_constraint_name` | `src/parse/rxt_schema.c` | none | `static`, decl removed |
| `pcrec_rxt_schema_opens_group` | `src/parse/rxt_schema.c` | **none anywhere, including its own file** | **left exported — dead, not touched** |
| `pcrec_rxt_source_ncols` | `src/parse/rxt_source.c` | **none anywhere, including its own file** | **left exported — dead, not touched** |

Five converted to `static` with their `internal.h` declaration deleted
(comment tied only to the declaration removed with it; each definition's
own header comment at the `.c` site is untouched, per the brief's "keep
its header comment"). `pcrec_dfa_axis_cands` had no `internal.h`
declaration to remove — it was already undeclared outside its own file,
just not `static`.

**Four are genuinely dead** — no caller anywhere in the tree, not even
inside their own translation unit — which the brief's carve-out says not
to delete ("deletion is a separate ruling"), so they are untouched and
still exported. One is worth a specific note: `pcrec_emit_abi_types`'s own
header comment says "exported for `emit_vm.c`", and its neighbor
`pcrec_emit_c_string_literal` (same comment shape, same file) genuinely
IS called from `emit_vm.c:10179` — so the pattern is real in general, but
this one instance was built for a cross-file call that never landed;
`emit_vm.c:10697` only mentions `emit_rx_abi_types` (the underlying
`static` function `pcrec_emit_abi_types` wraps) in a comment, never
calls the wrapper. A `D77`-shaped "built ahead of the need that never
arrived" instance, not a functional bug.

### Gate

- `make -j4 CC=gcc-16`: clean.
- `make strict CC=gcc-16`: **clean** ("strict: whole tree compiles clean
  with -Werror -Wshadow").
- `tests/spec_mod0/check01_isolation.sh . tests/spec_mod0/floors.txt`:
  **PASS** (36 symbol/TU pairs, 9 enabled-set symbols, 4 recogniser TUs,
  1 named exception) — unaffected by the ORG-7 linkage changes, as
  expected (this check is about the enabled-set symbol's isolation from
  recogniser TUs, not a general export census).
- `tools/review/function_census.py`'s output has no export/linkage
  column (columns are file/start_line/end_line/span_lines/code_lines/
  max_depth/name/header) — nothing to re-pin there; confirmed by reading
  the header row of `tools/review/out/function_census.tsv`.

## Validation (whole delivery)

| step | result |
|---|---|
| `make -j4 CC=gcc-16` | clean |
| `make strict CC=gcc-16` | clean ("whole tree compiles clean with -Werror -Wshadow") |
| `make test-codegen CC=gcc-16` | **65 checks passed, 0 failed; SABANCHOR sub-check: "all 270 sabotage rows' anchors resolve"; `run_group` 9/10 scripts passed** — the one non-passing script, `tests/codegen/run_inline_capability.sh` ("FAIL: nm could not read arm_a.o (no rx_search symbol) — no verdict is evidence here"), is a [CC-DIFF] VM-entry-chain-inlining capability probe wholly unrelated to this lane's changes (DFA closure invariants, five `static` conversions); **confirmed PRE-EXISTING by an A/B scratch build of the 82dd396a branch point**, which fails identically before any of this lane's edits exist. `make: *** [test-codegen] Error 1` is that one script's exit code, not a new failure. |
| `python3 scripts/m6read_check_sab_anchors.py` | **270 rows / 286 anchor sites, all anchors resolve** (was 269/285 before S262; the brief's assumed 285/285 gate value was the pre-lane baseline, now naturally 286/286 since this lane added one row) |
| `python3 scripts/emit_sweep.py --ref 82dd396a` | **0 movers, 0 asymmetric on all five streams, self-check passed** — see table below |
| `bash tests/mech/run_sabotage_matrix.sh S262` | **DETECTED** — `corpus:6190fail/22754pass`; `mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0)` |

**emit_sweep detail** (`--ref 82dd396a`, self-check first — an independent
second rebuild of the SAME ref, to prove the comparator itself is sound
before trusting its verdict on the real diff):

| stream | population | both_ok (reach) | both_refuse | movers | asymmetric |
|---|---|---|---|---|---|
| c-default | 3939 | 3518 | 421 | 0 | 0 |
| c-vm | 3939 | 3519 | 420 | 0 | 0 |
| emit-ir-vm | 3939 | 3519 | 420 | 0 | 0 |
| composition | 305 | 33 | 272 | 0 | 0 |
| dumps | 7 | 7 | 0 | 0 | 0 |

Self-check and real run (branch point `82dd396a` vs. this lane's built
`build/pcrec`) are row-for-row identical — 0 emitted bytes moved on any
stream, confirming the DFA_INVARIANT/`cx` threading and the five
`static` conversions change no emitted artifact, as the brief's proof
obligation required. `DELIVER witness: OK`. Elapsed 287.0s. Log:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/8f62ea75-43d2-4b00-8caf-d9b51bf26c8b/scratchpad/tour4_emit_sweep.log`.

## Re-pinned counts

- `scripts/m6read_check_sab_anchors.py`'s own live output (270 rows / 286
  sites) — this is COMPUTED, not hand-pinned, so nothing to edit; recorded
  above for the handback.
- Searched `docs/testing.md`, `tests/mech/CLAUDE.md`, and (per the
  brief's own grep) `grep -rn "269 rows\|269 sabotage\|269/" docs tests`
  tree-wide: every "269" hit found is either an unrelated test-count
  coincidence (`cli 269/0` — the CLI suite's own case count, nothing to
  do with sabotage rows) or a historical, dated narrative entry in an
  append-only file (`dev_journal.md`, `plan.md`/`plan_completed.md`,
  per-lane `docs/dev/lanes/*_report.md`) describing what a PAST run
  measured at that time — none of those are live counts and the
  Conventions in root `CLAUDE.md` treat `dev_journal.md` as append-only,
  so none were edited. **No living citation of "269"/"285" as the
  current sabotage population was found to re-pin** — the brief's
  assumption that such a citation existed (paired with the also-wrong
  S199 assumption) did not hold; noted here rather than silently
  skipped.
- `docs/dev/wake.md` is gitignored per the brief — not checked (would not
  be committed regardless).

## Files touched

- `src/ir/dfa.c` — the macro, its comment, the three call sites, the two
  new `cx` fields, `pcrec_build_dfa`'s `sc.cx = cx;`.
- `src/ir/CLAUDE.md` — one stale-comment correction.
- `docs/dev/known_issues.md` — K61.
- `docs/spec/match_api.md` — the "Two `abort()`s remain..." sentence
  corrected to "One", per manager ruling; headline sentence untouched.
- `tests/mech/sabotages/S262_dfa_invariant_loop_open_inverted.sh` — new.
- `src/core/tune.c`, `src/gen/emit_dfa.c`, `src/parse/mod_verbs.c`,
  `src/parse/rxt_schema.c` — five `static` conversions.
- `src/core/internal.h` — five declarations removed (four decl lines plus
  their tied comments; `pcrec_dfa_axis_cands` had none to remove).

## What is owed

Nothing from this lane's own validation list. All six steps (`make -j4`,
`make strict`, `make test-codegen`, the anchor gate, `emit_sweep.py
--ref 82dd396a`, the `S262` solo mech run) are complete, clean or
DETECTED as designed, with numbers recorded above. `make test` itself
(the full battery) is explicitly the manager's at merge, per BOILERPLATE.
