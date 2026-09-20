# [TOUR-2] lane report — vm_cost: cost_add/cost_max, the per-kind dispatcher, r61 F6

Branch `lane/tour2` (worktree `worktrees/tour2`), branch point `82dd396a`.
Design record: `docs/dev/reviews/2026-09-20-frank-tour.md` [TOUR-2]; F6 rides
here from `docs/dev/reviews/2026-09-20-r61-fable-personal-review.md`.

Four commits, one per step, each independently `make`/`make strict` clean:

- `4052f1a0` — step 1: `cost_add`/`cost_max` helpers, shared `vm_alt_flatten`.
- `6d72596d` — step 2: `vm_cost` becomes a per-kind dispatcher.
- `5e3b298a` — step 3 (r61 F6): `PCREC_NO_COUNTER` moves to `vm_counter_fits`'s callers.
- `f0e6cfa3` — re-aim S87/S95/S154 onto the extracted functions, intent re-verified.

`git diff --stat 82dd396a..HEAD`: `src/gen/emit_vm.c` (+/- 744 lines net of
the two-step rewrite), the three sabotage `.sh` files, `docs/dev/plan.md`
and `docs/dev/reviews/2026-09-20-frank-tour.md` (both from the manager's own
`6bc0a5bf` at the branch point, not this lane). **`src/opt/select_engine.c`
is untouched — zero lines changed** (see step 3 below for why).

## Step 1 — field-by-field arithmetic check, and the flatten-walk comparison

Read both blocks field by field before replacing, per the brief's own
instruction not to assume byte-neutrality:

- **A_CAT** was two six-line blocks (the spine loop over `t->r`, then the
  head `t`), each a **plain per-field SUM** (`frames`/`trail`/`pf`/`pt`
  added, `unbounded`/`growable` OR-ed) with no saturation, no special case,
  no field treated differently from the others. `cost_add(Cost *acc, Cost r)`
  reproduces that exactly.
- **A_ALT**'s fold was `c.frames = 1 + (c.frames > r.frames ? c.frames :
  r.frames)` **accumulated per branch**, not a one-shot max-of-all-branches-
  then-add-one: after branch *j* the running `c.frames` already carries every
  prior `1+`, so the true formula is `1 + max(1 + max(1 + max(f0,f1), f2),
  f3), ...)`, i.e. each chain level costs one frame on top of the deepest
  branch beneath it — matching `vm_alt`'s own chain shape (each level keeps
  one alternation frame live). `trail`/`pf`/`pt` were plain field-wise max
  with no `1+`. `cost_max(Cost *acc, Cost r)` takes the plain field-wise max
  (frames included, no `+1`); the call site then does `cost_max(&c, r);
  c.frames += 1;`, which mutates `c.frames` to `max(c.frames, r.frames)`
  first and THEN adds one — reproducing the accumulated fold exactly, verified
  by direct comparison of the two expansions rather than assumed. This is
  the "SUM versus ONE-PLUS-MAX" shape the brief asked to make visible: the
  `1 +` is deliberately left at the `vm_cost_alt` call site rather than
  folded into `cost_max`, so a reader sees the alternation's real shape
  where it belongs instead of inside a generic combiner.
- No field in either arm needed a special case (no saturating add, no
  clamping) — the plain sum/max shape holds exactly, so both helpers are
  unconditional field-wise operations.

**The flatten-walk comparison.** `vm_cost`'s A_ALT arm's inline branch-array
build (`emit_vm.c`, pre-refactor) and `vm_alt`'s own flatten at emission
(`emit_vm.c:4186` at the branch point) were **byte-for-byte identical** —
same five lines, same walk order, differing only in `&v->cx->arena` vs.
`&cx->arena` (where `cx = v->cx` in `vm_alt`). Confirmed by direct text
comparison before writing the helper, not assumed from the design record's
own hint. One shared `static int vm_alt_flatten(Ctx *cx, const Ast *a, const
Ast ***out)` (`emit_vm.c:2102-2113`) now backs both call sites — `vm_cost_alt`
and `vm_alt` — so the two walks cannot drift into disagreement about branch
order.

## Step 2 — the dispatcher's function list

`vm_cost` (`emit_vm.c:2694-2729`) is now a `switch` with one `case` per arm,
dispatching to:

| function | lines | shape |
|---|---|---|
| `vm_cost_kreset` | 2401-2406 | trivial body, comment-as-header |
| `vm_cost_cap` | 2411-2425 | trivial body, comment-as-header |
| `vm_cost_cat` | 2435-2445 | real body |
| `vm_cost_alt` | 2477-2498 | real body |
| `vm_cost_rep` | 2119-2379 | real body (pre-existing, unchanged) |
| `vm_cost_atomic` | 2530-2536 | trivial body, comment-as-header |
| `vm_cost_look` | 2592-2598 | trivial body, comment-as-header |
| `vm_cost_call` | 2657-2673 | real body |
| `cost_add` | 2070-2078 | helper (step 1) |
| `cost_max` | 2087-2095 | helper (step 1) |
| `vm_alt_flatten` | 2102-2113 | helper (step 1) |

The free-node kinds — `A_CLASS`, `A_EMPTY`, `A_BOL`, `A_EOL`, `A_END`,
`A_WORDB`, `A_NWORDB`, `A_GSTART`, `A_BREF` — stay **one shared zero-cost
case group inside `vm_cost` itself**, not split into individual functions,
per the brief ("a function returning zero for six kinds is ceremony"). One
change beyond the brief's own count: `A_BREF` was previously its own `case`
returning the identical zero `Cost` with its own separate comment block; it
is now merged into the same fall-through group as the other free kinds (both
explanatory comments preserved, concatenated, above the merged label list) —
the brief's own phrase groups backreference with the others as "one shared
`return c` group", so this merge completes what the switch already implied.

**Placement, and why it is not beside each `vm_<kind>` emitter.** The brief's
fallback ("if the file's banner sections make adjacency impossible, put them
together right before `vm_cost` and say so") applies here. `vm_cost_rep`
already established the precedent — it sits beside `vm_cost` (line 2119),
not beside `vm_rep` (line 5973, now shifted further by this change) — and the
emitters this step's other arms answer to are similarly far downstream, each
in its own feature-wave banner section: `vm_cap` (§M6.5.2, ~7972+shift),
`vm_atomic` (§M6.4.2, ~6242+shift), `vm_look` (§M6.6.2, ~6760+shift),
`vm_call`/`vm_splice` (§DD-14, ~7612/7727+shift). True per-kind adjacency
would mean scattering the whole cost pre-pass across thousands of lines and
several banner sections it does not otherwise belong to, breaking the file's
existing organization (the pre-pass section is grouped together on purpose —
`vm_count_slots`'s own dispatcher sits the same way, right after `vm_cost`).
All seven `vm_cost_<kind>` functions are therefore together, immediately
before `vm_cost`, exactly where `vm_cost_rep` already was.

**Headers.** Per coding_guide.md §4.2/[HDR-1]/[HDR-2] (first plain sentence,
then invariant/why-not-alternative, history pruned to a pointer): every new
function got a header. `vm_cost_call`'s header drops one paragraph of the
original in-switch comment — "[DD-14] A LOUD REFUSAL, not a number ...
UNREACHABLE IN THIS WAVE: nothing produces an A_CALL" — which was pure
wave-A2 history describing an arm that no longer exists (the code does not
refuse; it computes a real number with an over-charging fallback for the
one still-live guard case). Replaced with a one-line pointer to
`docs/design/subroutines_design.md` §4.4a/§5.7. Every other comment line
from the original arms is preserved verbatim in the new headers/bodies.

## Step 3 (r61 F6) — call sites touched

Grepped every caller of `vm_counter_fits` across the whole of `src/` (not
assumed from the brief's own wording) — **three, all in `emit_vm.c`, none
in `select_engine.c`**:

- `emit_vm.c:2163-2164` (`vm_cost_rep`'s counter arm, inside the combined
  `!vm_cursor_fits(...) && !vm_revdet_fits(...) && !(flags & PCREC_NO_COUNTER)
  && vm_counter_fits(v, a)` chain)
- `emit_vm.c:2855` (`vm_count_slots_rep`'s counter arm)
- `emit_vm.c:6064` (`vm_rep`'s real emission)

`select_engine.c` reads `PCREC_NO_REVDET` (its own `run_revdet`, the ANALYSIS
PASS driver that writes `u.rep.revbody`) but has **no call site of
`vm_counter_fits` at all** — confirmed by grep, not assumed from the brief's
"including select_engine.c" phrasing. The reason the two axes differ
structurally: `-fno-revdet` gates the pass that WRITES the eligibility fact
onto the AST node, so by the time `vm_revdet_fits` runs, a denied build
never produced a `revbody` for it to see — no flag check is needed inside
the predicate OR at its callers in `emit_vm.c`. The counter rung has no
separate analysis pass; its shape and its flag are both decided fresh at
each of the three `emit_vm.c` call sites, so the flag has to move there
directly. **`select_engine.c` is untouched by this commit — 0 lines
changed** — which is the safest possible outcome for lane tour5's
concurrent edit to `pcrec_select_engine`'s ladder in the same file: there is
nothing to conflict with.

Sanity-checked the deny axis still works post-move: `-fno-counter` on
`((a)|ab){0,12}c` under `--engine=vm` still changes the emitted VM program
(differs from the undenied build — confirmed via `diff`).

## Sabotage re-aims (S87, S95, S154)

Step 2's relocation staled three anchors —
`m6read_check_sab_anchors.py` went from **285/285 resolve** (pre-step-2) to
**3 STALE (282/285)** immediately after step 2's commit
(`S87_kreset_trail_uncharged`, `S95_atomic_trail_uncharged`,
`S154_call_trail_undercharged`, all in `emit_vm.c`). All three re-aimed onto
the new function bodies; **285/285 resolve again** after the re-aim commit.

Each re-aim is a verbatim relocation of the original SAB_BEFORE/AFTER text
(S87 and S95 dropped one level of indentation — switch-case body to function
top level; S154's anchor text is byte-identical, only its indentation
changed) — no plant text was altered in substance for any of the three.

**Intent re-verified LIVE**, not only by anchor resolution, for S87 and S95:
built a disposable scratch copy of the tree (`git archive HEAD`), applied
each sabotage via `tests/mech/lib/replace.py`, rebuilt, and matched a
deep-nested witness against both the sabotaged and the clean compiler.

| row | witness | baseline `RX_TRAIL_FRAMES` | baseline result | sabotaged `RX_TRAIL_FRAMES` | sabotaged result |
|---|---|---|---|---|---|
| S95 (atomic trail uncharged) | `(?:(?>a)){2000}` on 2000 `a`s | 2253 | `match 0 2000` | 253 | `frames` (PCREC_ERR_FRAMES) |
| S87 (`\K` trail uncharged) | `(?:a\K){0,500}b` on 500 `a`s+`b` | 1003 | `match 500 501` | 503 | `frames` (PCREC_ERR_FRAMES) |

Both reproduce the row's own documented failure mode exactly: the sabotaged
compiler under-declares trail capacity by one entry per emitted charge site
and the identical pattern/subject that matches cleanly on the real compiler
now returns a typed give-up.

**S154 (call trail undercharged) was verified by clean apply + rebuild
only** — the sabotage applies at its expected single occurrence and the
sabotaged compiler builds warning-clean — **not** by a live match
differential. `^(a(?1)?b)$` over `a^n b^n` (the row's own documented
bisection witness) turned out to hit a fixed bring-up trail default
(`RX_TRAIL_FRAMES 3072`, the DD-14.FB placeholder for a cyclic/unbounded
target) at every `n` tried before the sizing difference between `2*|W|` and
`|W|` could show through — both the baseline and a first attempt already
answered `frames` at `n=200`, so that specific witness cannot discriminate
the two builds at all. Finding a finite, non-cyclic call-chain witness whose
trail sizing is genuinely COMPUTED (rather than defaulted) needs more
construction than this lane's remaining time budget allowed; **owed**.

## Validation

- `make -j4 CC=gcc-16` — clean, zero warnings, after every commit.
- `make strict CC=gcc-16` — clean (`-Werror -Wshadow`), after every commit.
- `python3 scripts/m6read_check_sab_anchors.py` — **285/285 resolve** (final state).
- `python3 scripts/emit_sweep.py --ref 82dd396a` — **0 movers / 0 asymmetric
  on ALL FIVE STREAMS**, both the self-check (independent rebuild of the ref)
  and the real run (ref vs. this branch's `build/pcrec`): `c-default`,
  `c-vm`, `emit-ir-vm`, `composition`, `dumps`. Population: 3,939 corpus
  pattern rows, 305 composition files, full reach (3,518-3,519 both-ok per
  `.c` stream, 33/98 composition producing/artifacts, 7/7 dumps). Elapsed
  312.3s. Log: `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/8f62ea75-43d2-4b00-8caf-d9b51bf26c8b/scratchpad/tour2/emit_sweep.log`.
- **Size log by-column comparison** (the brief's second proof column):
  `bash tests/size/run_size_log.sh` (full corpus) wrote 3,481 rows at this
  branch's tip (`5e3b298a` at the time it ran); `scripts/size_diff` against
  a pre-lane baseline (`docs/dev/artifact_size_log.tsv` as committed at
  `d5d5cfd0`, one commit before this lane's branch point, verified an
  ancestor of `82dd396a` with no intervening `src/` changes) reports **0
  patterns moved, 0 vanished, 0 new, total `size_bytes` IDENTICAL
  (115349289 == 115349289)** — the stamped ceilings (and everything else
  the log tracks) did not move by column, corroborating `emit_sweep`'s
  byte-exact result with a second, independent instrument. The regenerated
  `docs/dev/artifact_size_log.tsv` was reverted (`git checkout --`) per the
  manager's instruction — a warm-box regeneration, not committed. Backup of
  the OLD baseline and the diff output:
  `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/8f62ea75-43d2-4b00-8caf-d9b51bf26c8b/scratchpad/tour2/artifact_size_log_OLD_d5d5cfd0.tsv`,
  `.../size_diff_result.log`.
- `make test-codegen` — **9/10 scripts pass, 301 individual checks, 0
  failures.** The sole red, `run_inline_capability.sh` ("FAIL: nm could not
  read arm_a.o (no rx_search symbol) — no verdict is evidence here"), is
  **confirmed pre-existing**: reproduced identically on a from-scratch build
  of the pristine branch point `82dd396a` with none of this lane's changes
  applied. Not this lane's. Log:
  `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/8f62ea75-43d2-4b00-8caf-d9b51bf26c8b/scratchpad/tour2/test_codegen_full.log`.
- **Counter axis (`make test-axes`) — OWED, not a timing decline.** Launched
  as the brief allowed ("if the full axes run exceeds ~4 min, make it your
  LAST launch"); discovered mid-run that lane `tour5` was concurrently
  running its own `make test-axes` on this box (its brief's own proof
  column) — a genuine box-concurrency collision under the one-heavy-suite-
  at-a-time rule. Killed my instance via `scripts/safekill` (16 processes
  across 5 groups, clean) rather than let two full-corpus axis sweeps
  contend, and did not relaunch. The counter axis's own answer-identity
  claim is unchanged by this move in the FIRST place — `PCREC_NO_COUNTER`
  still denies exactly the rung it always did, at exactly the population it
  always did (verified functionally above, sanity-check paragraph) — so
  this is corroborating evidence owed, not a live risk.
- `make test` — **not run**, per the brief ("Do NOT run the full `make
  test`").

## Anomaly noted, not acted on

Partway through this lane's work a system environment update reported this
session's "primary working directory" as `worktrees/tour5` rather than
`worktrees/tour2`. Every command in this lane's session was issued with an
explicit `cd /Users/fdicostanzo/pcrec/worktrees/tour2 &&` prefix regardless
of any default cwd, and every commit's `git log`/`git status` output
throughout confirms all work landed in `worktrees/tour2` on `lane/tour2` —
so nothing in this delivery was affected. Flagging it in case it signals a
harness-level cwd-tracking issue worth the manager's attention.

## Summary

Validation COMPLETE except the counter-axis `make test-axes` corroboration
(owed — box collision with tour5, not re-launched) and S154's live
match-differential (owed — needs a better witness than the row's own
documented one). Everything else: byte-neutral by construction and MEASURED
so on two independent instruments (`emit_sweep.py` 0/0 on five streams,
the size log 0 movers/byte-identical total), `make -j4`/`make strict`
clean, sabotage anchors 285/285 with two of three re-aims verified live
against the exact predicted failure mode, `make test-codegen` 9/10 with the
sole red confirmed pre-existing against the branch point. `src/opt/select_engine.c`
untouched (0 lines) for lane tour5's concurrent edit.
