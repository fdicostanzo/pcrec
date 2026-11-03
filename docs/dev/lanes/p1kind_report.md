# Lane p1kind — lm_has_kind with no `default:` (the landmark walk's g1 \G/\K read)

Lane p1kind, opus, 2026-10-30, worktree `worktrees/p1build` (branch `lane/p1build`). Fixes the
`test-cpset-structure` red `[5c]` (a `default:` on an AKind switch in `src/gen/lmwalk.c`'s
`lm_has_kind`) and answers the brief's question: could that walker MISS a nested `\G`/`\K` and
let the walk give a wrong answer?

## Answer: no wrong answer was possible; the fix is structural

1. **No existing fact.** The `kinds` fact mask (`src/facts/kinds.c`, `PF_KIND_ROWS`) has no
   `\G`/`\K` bit and the parser records no such fact (`first_kreset_pos` in `core/internal.h`
   only supplies a diagnostic's offset). The general mechanism for the walk is
   `pcrec_ast_visit` (`core/internal.h`): coding guide §2.4 names it "the ONE home for the
   generic pre-order whole-tree visit". `lm_has_kind` now runs through it: one exhaustive
   switch with no `default:`, the spines walked iteratively (the old walker recursed on
   `A_CAT`'s left spine), and `u.call.body` not followed (a callee is visited at its own
   lexical position).
2. **The old walker missed nothing in today's AKind.** Its `default:` covered `A_CLASS`,
   `A_EMPTY`, `A_EOL`, `A_CTX`, `A_GSTART`, `A_KRESET`, `A_BREF`, `A_VAR`, `A_CALLOUT` and
   `A_CALL`. `pcrec_ast_visit` treats every one of those as a leaf (`A_CALL`'s body is the back
   edge every whole-tree walk declines), and it descends the same seven kinds the old switch did
   (`A_CAT`, `A_ALT`, `A_REP`, `A_CAP`, `A_ATOMIC`, `A_WCLASS`, `A_LOOK`). Conditionals
   `(?(1)..)` are not an AKind: the parser refuses them ("module 'conditionals' ... is not
   implemented yet"). DEFINE is an `A_REP {0}`, named groups are `A_CAP`, lookbehind is
   `A_LOOK`. The old function's defect was that it was not exhaustive (a new kind with children
   would have been skipped silently, the `[5c]` rule) and that it recursed on spine length. It
   did not have a reachable miss.
3. **No live `\G`/`\K` reaches row g1 at all.** A live `\G` puts `N_GSTART` in the NFA, so
   `pcrec_nfa_has_bot` sends the pattern to the attempt engine and the walk is never asked. A
   `\G` in a lookaround makes the finisher a VM, so row 1 `finisher-dfa` declines first. `\K`
   is a VM-only registry row, so it also declines at `finisher-dfa`, even inside a DEFINE or a
   `{0}` body. The only `\G` that reaches g1 is a DEAD one: inside a `{0}` body, which the NFA
   build erases. There g1's `gstart` decline is conservative, and the answer would be the same
   either way.

Because of (2) and (3), the witnesses below show the SAME walk decision before and after the
fix, and every answer matches libpcre2 before and after. The sabotage plants the bug class
(a walker that descends into nothing), and its detector is structural: the walk is admitted
where g1 must decline. No answer can detect it today.

## Witnesses

"Before" is the trace build of the tree at `dcb0d68ee` (the old switch). "After" is the trace
build with the fix. Both use `PCREC_LMWALK_TRACE=1` with the `-DPCREC_CAND_TRACE` build in
scratch. Answers come from `tests/landwalk/landwalk.rxt` (generated from libpcre2 10.46 by
`gen_landwalk.py`, re-checked by `tests/revend/verify_stage2.py`: 207 cells agree, 0 FAIL) and
pcrec's harness on the fixed build (207 passed, 0 failed).

| pattern | where the `\G`/`\K` sits | walk before | walk after | answers vs libpcre2 |
|---|---|---|---|---|
| `[a-z]+@x(?:\G){0}` | `{0}` body, suffix | g1/gstart | g1/gstart | 5/5 agree (new cells) |
| `(?:\G){0}[a-z]+@x` | `{0}` body, prefix head | g1/gstart | g1/gstart | 5/5 agree (new cells) |
| `[a-z]+@x(?(DEFINE)(?<g>y\G))` | named group in a DEFINE | g1/gstart | g1/gstart | 4/4 agree (new cells) |
| `[a-z]+@x(?:(y\|\G)+){0}` | alternation in a repeated capture in `{0}` | g1/gstart | g1/gstart | 4/4 agree (new cells) |
| `[a-z]+@x(?:[yz]\G){0}` | after a class in `{0}` | g1/gstart | g1/gstart | 4/4 agree (new cells) |
| `[a-z]+@x(?(DEFINE)(?<k>\K))` | `\K` in a DEFINE named group | finisher-dfa | finisher-dfa | 4/4 agree (new cells) |
| `[a-z]+@x(?:(?>\G)){0}` | atomic in `{0}` | finisher-dfa | finisher-dfa | probe only |
| `[a-z]+@x(?:(?=\G)){0}`, `(?:(?<=\G)){0}` | lookaround in `{0}` | finisher-dfa | finisher-dfa | probe only |
| `[a-z]+@(?=\G)x`, `(?<=\Ga)[a-z]+@x` | live lookaround | finisher-dfa | finisher-dfa | probe only |
| `[a-z]+@x(?:\K){0}` | `\K` in `{0}` | finisher-dfa | finisher-dfa | probe only |
| `[a-z]+@x(?:(?C1)\G){0}` | after a callout | VM (walk not asked) | same | probe only |
| `[a-z]+@x(?(1)\G\|y)` | conditional | refused (module not implemented) | same | n/a |
| `a+@\Gx`, `a+@(?<n>\Gx)`, `(?:\G)?a+@x` | live `\G` | attempt engine (walk not asked) | same | probe only |

So no witness was a wrong answer before the fix. The STOP RULE (another g-condition walker with
the same `default:` flaw that gives a wrong answer) did not fire. `lm_maxw` in the same file is
already an exhaustive switch with no `default:`. It and `lm_flatten` still recurse on the `A_CAT`
spine (the K20 shape). A pattern long enough to matter does not reach them today: a
20,000-byte and a 120,000-byte literal prefix overflow the DFA before the walk is asked (no
`LMWALK` trace record). This is noted here, not changed.

## Changes (branch `lane/p1build`)

- `src/gen/lmwalk.c`: `lm_has_kind` runs through `pcrec_ast_visit` (callback `lm_kind_seen`,
  ask record `LmKindAsk`). No emitted byte moves and no stamp moves: a decision-identical
  rewrite.
- `tests/landwalk/gen_landwalk.py` + regenerated `tests/landwalk/landwalk.rxt`: six D-family
  blocks (the table's first six rows). The rest of the file regenerates byte-identical.
- `tests/codegen/run_landmark_walk.sh`: five g1/gstart witnesses (expected `"unanchored"`, the
  deny byte-identity arm included). The declining-witness floor goes from 12 to 17.
- `tests/mech/sabotages/S1855_lmwalk_gstart_root_only.sh`: the plant asks the root node only
  (`lm_kind_seen(&q, a)` in place of the visit). Its detector is the five witnesses (arm
  `landwalk`). `VALIDATE_ONLY=1` reports 1 definition valid. S1850-S1854 were fsfix's range
  (fsfix used S1853 as a manual sabotage), so this row takes S1855.
- `tests/startset/manifests/manifest_s2_vm_forced.tsv`: re-pinned with p1pin's method
  (`census_s1.py` on the lane build, scratch `p1kind/census`). +6 rows (the new blocks as
  forced-VM movers). Two existing landwalk rows were renumbered by the insertion (:363 to :419
  and :372 to :428, same text). The corpus diff against the census is empty. `s2_vm_auto` and
  `s3_dfa` did not move.

## Validation

- `make strict`: clean (`-Werror -Wshadow`).
- `scripts/boxlock run --label p1kind-test-cpset-structure -- make test-cpset-structure`:
  rc 0, `PASS: [5c] no AKind switch carries a default:`, no `*** [test-` line.
- `bash tests/codegen/run_landmark_walk.sh` (worktree build): 78 passed, 0 failed.
- `bash tests/harness/run.sh tests/landwalk/landwalk.rxt`: 207 passed, 0 failed.
  `tests/revend/verify_stage2.py` on it: 207 agree, 0 FAIL.
- `scripts/boxlock run --label p1kind-test-codegen -- make test-codegen`: rc 0, `run_group: 20/20
  scripts passed`, no `*** [test-` line (`run_landmark_walk.sh` rides here).
- `scripts/boxlock run --label p1kind-test-startset -- make test-startset`: rc 0, `[vm-movers]` vm
  3759 rows (3753 + 6) and `[dfa-movers]` 59 rows, both 0 off-diagonal, no `*** [test-` line.
- Mech `bash tests/mech/run_sabotage_matrix.sh S1855`: `landwalk:10fail/68pass DETECTED` (the five
  witnesses read "landmark-walk", and their five deny byte-identity arms move with them), `== mech
  run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0 ...)` at 65536e720.
- Logs: `$PCREC_TMPDIR/scratch/p1kind/` (`test-*.log`, `mech.log`, `census.log`, `harness.log`).

## STATE AT HANDOFF

- STATE: done. Branch `lane/p1build`. Commits e766f6b15 (fix, witnesses, sabotage), the manifest
  re-pin, 0fbe9b4d1 (S1855 renumber), 65536e720 (report WIP), and this report's final commit.
- Rulings file `p1kind_rulings.md`: read at every commit. The last entry is "(none yet)", so no
  ruling was applied.
- Nothing is OWED by this lane. The full `make test` on this tree is the already-queued
  `709-p1tri-test` (not before 2026-10-31T08:00). It runs on the tree at run time, so it covers
  these commits. `711-p1build-mech`'s id list does not name S1855. The manager may add it there;
  the row is already measured DETECTED above.
- Not changed, noted: `lm_flatten` and `lm_maxw` recurse on the `A_CAT` spine. Today the walk is
  not reached by a pattern long enough to matter (the DFA overflows first). A `kinds`-fact bit for
  `\G`/`\K` was considered and not built: it would be an observable `--emit-facts` change with a
  spec hunk for a decision-identical fix. `pcrec_ast_visit` is the guide's named home.
