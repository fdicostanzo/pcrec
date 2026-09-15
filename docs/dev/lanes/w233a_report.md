# [DD-13b.W23.3a] — `include`'s harness half (lane w233a)

Branch `lane/w233a`, from `lane/w233` tip `6edfba46`. Step brief:
`docs/design/dd13_format/w23_impl.md` REVISION 1.1 §6.3a; mechanism
§1.10; design of record `format_design.md` 3.4.2 §2.5/§2.11. Six
commits: `4fd013c3` (leg A), `426c974c` (leg B), `da0b80c6` (leg C +
spec hunk), `72dbfbe8` (first session-close report), then the fixtures
+ W23-S7 + S247 + SW20 wave (this revision — see §0 for the manager's
ruling that authorized finishing in this same lane rather than a fresh
one).

**STATUS: DELIVERED.** §3's OWED list from the first session-close
report is now DISCHARGED item by item, §3.1 below. `make strict`
clean; `tests/rxtsource/run_rxtsource_tests.sh` **184 passed / 0
failed** (up from 175 — the 9 new checks are named in §3.1); census
**210/3936/28943 unchanged**. `make test`/`test-axes`/`san`/`lint`
remain OWED to the next battery — the box constraint named in the
brief held for this lane's entire working period.

---

## 0. Rulings received

**One ruling, delivered as a teammate message, ACCEPTED IN FULL and
consumed exactly as stated:**

> RULING on the leg-C finding: ACCEPTED. The structural reading is
> right and matches the r59-A2/dup_head_description precedent exactly
> — an include-bearing file is head-bearing by construction, so leg
> C's half is discovery subtraction only. Write W23-S7 per your
> corrected reading: the splice half compares legs A and B;
> include_dup_path uses check_refusal (single-leg, leg A) with a
> comment stating the seam-ruling reason, dup_head_description's own
> wording pattern. Where leg B surfaces a [resolution]-class failure,
> assert that class explicitly in the same check. Record the ruling in
> your report's "Rulings received" section, and note that the
> w23_impl.md §1.10.2 symmetric-legs sentence and W23-S7's acceptance
> line get their correction AT THE MERGE by me (cite the exact lines
> in your report; do not edit the note yourself — w232's precedent).

Consumed as: §2 (unchanged from the first report — the finding stands)
+ W23-S7 built as a leg-A/leg-B differential for `include_basic` and
`include_nested`, `include_dup_path` on `check_refusal` (single-leg,
`dup_head_description.rxtin`'s wording pattern, §3.2 fixture table
below), and a THIRD instrument — a scenario built inline in
`run_rxtsource_tests.sh` rather than as a fourth named fixture (§3.1
item 1's own reasoning) — that exercises leg B's `[resolution]` tag
explicitly on a cross-file duplicate (two different includers reaching
one shared fragment), which is the one shape `include_dup_path`'s
same-file collision cannot reach (leg A refuses the entry's own
`--list-source` call before `rxt_expand_closure` ever runs).

**The lines the manager corrects `w23_impl.md`/`format_design.md`
against, at the merge (I do not edit the ruled note myself):**

- `docs/design/dd13_format/w23_impl.md` §1.10.2's table, the "legs B
  and C" cells of rules 2 ("REPORT"), 4 ("SPLICE") and 5 ("CLOSURE
  TALLY") — each should read "leg B; leg C's half is discovery
  subtraction only" for the reason §2 below states.
- The same note's §3.1 W23-S7 row and its §6.3a acceptance list
  ("three independent runs" / "the three legs' block counts are
  equal") — the splice half is a two-leg (A/B) comparison, never
  `check_refusal_all3`'s three-way shape.

---

## 1. What is built and MEASURED

### 1.1 Leg A — the `include` row didn't exist; now it does (§6.3a item 1)

**§6.3a's own item 1 was wrong about the starting state, and it says so
in words that predict the fix**: "a COLUMN on a row W23.3 already
emits — not a new row kind". MEASURED against the actual W23.3-built
tree: `include` parsed and was DROPPED — no `RxtRow`, per
`rxt_source.c`'s own comment ("RECOGNISED, value-checked and DROPPED
... none of them pushes an RxtRow") — and
`docs/spec/rxt_format.md`'s pre-existing column table listed only
`lib`/`target`/`config`/`description`/`pattern` as `kind`s. §2.2's own
escape hatch ("if it finds itself editing `rxt_source.c`, the row is
missing and the boundary is wrong") names exactly this gap; the
correct reading, verified against the actual dump columns, is that
NO NEW COLUMN was needed (kind/line/name/value are all pre-existing),
so the "one src/ touch" the item already budgeted for was right in
SIZE, wrong in DESCRIPTION.

`RXT_DECL_INCLUDE` lands (`src/core/internal.h`). `include "path"` now
pushes a row: `value` = the path AS WRITTEN (`lib`'s own convention,
quotes kept), `name` = the RESOLVED REAL PATH — `realpath(3)`,
NULL-buffer form, computed AT PARSE TIME. This is a deliberate
departure from `lib`'s "the head parser touches no filesystem"
contract, because `--list-source` is the ONLY call legs B and C ever
make over an `include` line (§1.10.2 rule 2) — a resolution only
`--source`'s separate `pcrec_rxt_source_resolve` could see would leave
them nothing to read.

Two refusals, both new: an unresolvable path (`value-shape`, `lib`'s
own wording pattern) and a SAME-FILE duplicate resolved path
(`schema-constraint`, naming both lines) — the one slice of §2.5's
closure-wide duplicate rule a single file's own parse can decide
without walking anything else (the cross-file half is legs B/C's, over
the closures they walk).

**Verified**: `make`/`make strict` clean throughout. The committed
fixture `include_dup_path.rxtin` (§3.2) exercises the duplicate
refusal directly, naming both lines, through `check_refusal` in
`tests/rxtsource`. `include_basic.rxtin`/`include_nested.rxtin`
exercise resolve. Census 210/3936/28943 unchanged (the shipped corpus
still has zero `include` lines, so the new row kind has no population
there — exactly the corpus control §1.10.3 predicts).

### 1.2 Leg B — subtraction, splice, tally, the fourth failure class (§6.3a items 2-5, 7)

`tests/harness/run.sh` gains, in dependency order:

1. **Entry-set subtraction** (§1.10.2 rule 3), run ONCE over the whole
   discovered set before either dispatch branch: a lightweight
   `rxt_head_probe` (factored to match the per-file loop's own test
   exactly), a `pcrec --list-source` call on every head-bearing
   candidate (cached — see below), and a filter that drops any
   discovered file whose own resolved path is the target of ANOTHER
   discovered file's `include` row. Rule 6's "named, absorbed into
   `<entry>`" fires only for a file that reached `files[]` via a bare
   argv token (tracked separately from a directory walk's own finds).

2. **Splice** (§1.10.2 rule 4), NOT by concatenating text into one
   combined stream. Rule 5 requires a failure to print the FRAGMENT's
   own `file:line`, and the existing per-file loop's diagnostics are
   threaded through its whole pinned arm chain via `$file`/`$lineno` —
   remapping that would have meant touching every diagnostic site in
   ~800 lines of hash-pinned code for one step. Instead: each entry's
   closure is walked depth-first (`rxt_expand_closure`, `closure_walk`'s
   sibling one leg over) and its fragments are INSERTED into `files[]`
   right after it. The existing per-file loop is **UNCHANGED** — a
   fragment is just another array element to it, so `$file` is
   genuinely that fragment's own path and every diagnostic is correctly
   attributed for free. This also settles PROCS>1 for free: subtraction
   runs before dispatch (so a fragment is never spawned as its own
   top-level worker) and splice runs inside each worker's own
   re-invocation (so a fragment runs as part of its entry's own turn,
   never as an independent sibling) — no code shared between the two
   phases needed to know about the other.

3. **The fourth failure class** (§2.11): an unresolved include, a
   same-closure duplicate, or a cycle anywhere in an entry's closure
   walk is tagged `[resolution]`, scored into `compile_fail_set`
   exactly as an ordinary whole-pattern compile failure is (rule 7:
   "scored as a pattern-compile failure"), attributed to the ENTRY at
   line 1 (rule 1: "the tally is the entry's"). An entry whose closure
   fails still runs its OWN body — a broken fragment must not silently
   delete the entry's own cases too.

4. **Two new summary lines**, both blocks (serial and PROCS>1's own
   aggregation): `entry files: N`, `fragments spliced: M`. A THIRD
   place they had to be taught to print: `--dump` mode's own early
   return, TO STDERR (never stdout — `--dump`'s stdout is what the C1
   differential compares byte for byte, so joining the rows there would
   corrupt the comparison). This is what lets the CORPUS CONTROL
   (§1.3 below) run cheaply, at zero compile cost, over the whole
   corpus.

`rxt_list_source_cached` (one `--list-source` call per file, shared by
subtraction, expansion, and the pre-existing per-file head-detection
call it now routes through too) needed two real bug fixes before it
worked, both caught by `tests/rxtsource`'s own count checks
(`head`/`sem10`, "`--list-source` called exactly once"):

- **Subshell caching is a no-op.** The first version cached via
  `x="$(fn ...)"` — command substitution forks a subshell, so the
  cache's `assoc_set` write vanished the instant the subshell exited
  and EVERY call was a real re-invocation (3 calls per file where 1
  was expected). Fixed: the function sets a global `RXT_LS_OUT`
  instead of printing, called directly with no `$(...)`.
- **`cd DIR && pwd` is LOGICAL, not the resolved path `realpath(3)`
  gives.** macOS's `/tmp` is a symlink to `/private/tmp`; plain `pwd`
  does not resolve it, so the subtraction pass's own key computation
  silently disagreed with leg A's `name` column and every
  cross-directory include-target lookup missed. Fixed:
  `rxt_realpath()`, using the `realpath` command (present on this box
  and on Linux coreutils) with a `cd`+`pwd -P` fallback.

### 1.3 Leg C — discovery subtraction only, and the finding on why (§2, unchanged)

`verify_rxt.py`'s `discover()` gains the same entry-set subtraction as
leg B: `_rxt_head_probe` (the identical cheap test), `_rxt_list_source`
(subprocess call to `pcrec --list-source`, cached by
`os.path.realpath` — python's own `realpath(3)` binding, so it agrees
with leg A's `name` column by construction, with no `cd`+`pwd`-style
trap to fall into), and a filter identical in shape to leg B's. Prints
the same `"<file>: named, absorbed into <entry>"` line for a bare
argv-named file that gets subtracted. **NO SPLICE HERE** — see §2.

---

## 2. THE FINDING: leg C cannot splice, and §1.10.2's table over-states its own symmetry

§1.10.2's table lists "legs B and C" together for rules 2, 4 and 5 —
report, splice, and per-fragment failure attribution — reading as
though both harness legs gain the same closure-walking capability.
**MEASURED, this is false for leg C, structurally, not by omission.**

`include` was added to `parse_rxt`'s `head_words` tuple at W23.3 (it
is genuinely head-scoped — there is no other place it could sit). Any
file whose first body-scope token is `include` is therefore
**head-bearing**, and `verify_rxt.py`'s seam ruling — "a head-bearing
`.rxt` file is not verifiable by this script in this build" — already
refuses every such file with an uncaught `ValueError`, in BOTH plain
verification mode and `--dump` mode. Verified live on this branch:

```
$ python3 tests/harness/verify_rxt.py entry.rxt    # entry.rxt: include "frag.rxtfrag" ...
Traceback (most recent call last):
  ...
ValueError: entry.rxt:1: 'include' is a file-level (HEAD) declaration...

$ python3 tests/harness/verify_rxt.py --dump entry.rxt
Traceback (most recent call last):
  ...  (same ValueError, --dump mode calls parse_rxt with no guard either)
```

This is **the same disposition class w233's own report already
recorded for `ext` at file scope** (§3.1 there: "Those two clauses
cannot both hold at any point in W23... `ext` at FILE scope is a HEAD
declaration; the head has exactly ONE parser by the seam ruling;
`aux_arbitrary_keys.rxtin` keeps its FILE-scope `ext` and is leg A
only"). It recurs here for the same underlying reason — a head-scoped
production's file is, by the seam ruling, off-limits to legs B and C's
own parsers — except `include` cannot be moved to block scope to avoid
it (§2.5 makes it a head declaration by design: it splices FILES, not
lines within a block).

**Consequence for the delivery**: leg C's role for `include` is
`discover()`-level subtraction ONLY — keeping its own population
honest (not double-verifying a `.rxt`-extension fragment that is also
someone's include target) — never a three-way block-count comparison
with legs A and B for an `include`-bearing entry. §1.10.2's row-2/4/5
"legs B and C" phrasing should read "leg B; leg C where its own
head-bearing refusal does not already apply, which for `include`
specifically is never". W23-S7's acceptance line as written — "the
three legs' block counts are equal" — is **unbuildable as stated**
for the closure/splice half, on the same grounds `dup_head_description`
and `aux_arbitrary_keys` already established: a head-bearing fixture
gets `check_refusal`'s single-leg treatment, or in this case a
two-leg (A+B) comparison, not `check_refusal_all3`'s three-way one.
**RULED (§0): ACCEPTED, and W23-S7 is built to this corrected reading.**

**What this does NOT affect**: leg A and leg B's OWN mechanisms are
independently verified and do not depend on leg C's participation. The
corpus control (§1.10.4's "0 fragments spliced, entries ==
CENSUS_FILES") is satisfied by leg C's subtraction alone — and,
separately, by leg B's own `--dump` run over the corpus (§3.1 item 4).

---

## 3. The owed list, discharged

### 3.1 What each item became

1. **The three fixtures, COMMITTED** in `tests/rxtsource/fixtures/`:
   `include_basic.rxtin` + `include_basic_frag.rxtfrag` (flat splice,
   one fragment); `include_nested.rxtin` + `include_nested_frag1
   .rxtfrag` + `include_nested_frag2.rxtfrag` (two deep — frag1
   includes frag2, "in include order, depth first" needs a second
   level or a flat splice proves nothing about it); `include_dup_path
   .rxtin` (reuses `include_basic_frag.rxtfrag` as its collision
   target — a resolved-path collision needs a target, not a property
   of the target). The `.rxtfrag` siblings are copied VERBATIM into
   `tests/rxtsource`'s scratch run directory (extension kept, never
   renamed to `.rxt`) — `run_rxtsource_tests.sh`'s own fixture-copy
   loop gained a companion `*.rxtfrag` pass, since the pre-existing
   loop only ever handled `*.rxtin` -> `.rxt`.

2. **W23-S7, built** in `run_rxtsource_tests.sh`, per §0's ruling:
   `check_include_splice FIXTURE DIRECT TOTAL LABEL` asserts THREE
   independent numbers per fixture (leg A's own direct include-row
   count on the entry; leg B's `entry files`/`fragments spliced`; the
   case-count arithmetic `1 + TOTAL`) for `include_basic` (1/1) and
   `include_nested` (1/2 — leg A's own count on the ENTRY stays 1
   because a nested fragment's own include is invisible to a single
   `--list-source` call on it, exactly as it is invisible to any one
   node of `closure_walk`'s own recursion). `include_dup_path` runs
   through `check_refusal` (single-leg, `dup_head_description.rxtin`'s
   own wording pattern), asserting the refusal names BOTH lines. The
   `[resolution]`-class scenario (§0's third instrument) is built
   INLINE as three scratch files under `$WORKDIR` — two different
   includers reaching one shared fragment — on the W23.4 item 3b
   "synthetic stream in the repair's own commit" precedent, asserting
   the `[resolution]` tag appears AND the entry's own body still runs
   (`cases failed: 1`, never more). **9 new checks, all green**:
   `checks passed: 184` (was 175).

3. **S247, committed**: `tests/mech/sabotages/
   S247_include_closure_not_recursive.sh` deletes `rxt_expand_closure`'s
   own recursive call, so a fragment's OWN nested includes are
   silently never followed. Detects `include_nested` (`fragments
   spliced` 2 -> 1) and leaves `include_basic` (nothing at depth two to
   lose) and the corpus control (zero include lines to begin with)
   green — the exact FIXTURE-arm-red/corpus-arm-green split §6.3a's
   acceptance line names. `VALIDATE_ONLY=1 bash tests/mech/
   run_sabotage_matrix.sh S247` — **FIELDS OK**. HAND-VERIFIED DETECTED
   on a scratch build: the plant applied IN PLACE to a throwaway copy
   of `run.sh` (a copy OUTSIDE the repo breaks `ROOT_DIR` resolution
   and reports nothing meaningful — recorded here because it cost a
   debugging round before the right methodology was used) reproduces
   exactly the predicted numbers, then reverted cleanly (`git diff`
   confirmed empty against the pre-plant tree). **Highest id on
   `main`: S244** (`git ls-tree -r main -- tests/mech/sabotages`);
   this branch's own history additionally carries S245/S247 from
   unmerged W23 lanes (S240/S241/S244/S245 from w231/w233, this
   lane's own S247) — S247 collides with nothing on `main` or in
   this worktree, whose own highest id before it was S245.

4. **The census pin's second number, asserted explicitly**: item 2 of
   this list's `check_include_splice` calls already give leg A/leg B
   their own numbers per fixture; the CORPUS-WIDE assertion is a new,
   separate check — `entry files: $CENSUS_FILES` (210) / `fragments
   spliced: 0` over the WHOLE corpus, run through `bash run.sh --dump
   "$ROOT_DIR/tests"` rather than a bare full run (this section's own
   header says it is cheap because it compiles nothing; a bare
   `bash run.sh` over 210 files would duplicate `test-corpus`'s own
   compile workload inside a section built specifically not to compete
   with it for the box — `--dump` still walks every file through
   subtraction and splice, parsing only, which is everything this
   control needs). This is why leg B needed the third `--dump`-mode
   printing site (§1.2 item 4).

5. **SW20, landed**: `docs/spec/rxt_format.md`'s "How the harness
   evaluates a block" section gains the cell notion, `include`'s
   accounting-unit rules (1-3, restated as testable claims), the two
   new summary lines, and the RESOLUTION failure class. MEASURED after
   landing: `grep -c "entry files\|fragments spliced\|RESOLUTION
   failure" docs/spec/rxt_format.md` finds all three — the FIRST
   attempt at this hunk had "entry files" and "resolution failure"
   silently split across a markdown line-wrap and grep missed them
   (the exact silent-drift shape SW20's own charter is about, caught
   before commit only because the obligation says "grep for it", not
   "write prose about it" — the check IS re-reading the file with the
   same command the obligation names).

6. **§6.3a's acceptance line, satisfied**: "S247 turns W23-S7 red on
   the FIXTURE arm and leaves the corpus arm green" — VERIFIED by hand
   (item 3 above), since S247's own field-only validation cannot run
   the full sabotage matrix under the current box constraint (a fresh
   `git archive HEAD` tree build); the real mech-matrix `DETECTED`
   figure rides the next battery, per this lane's own OWED note below.

### 3.2 The committed fixture table

| fixture | what it makes reachable |
|---|---|
| `include_basic` + `include_basic_frag.rxtfrag` | §1.10's whole mechanism in one cell: flat splice, one fragment |
| `include_nested` + `include_nested_frag1.rxtfrag` + `include_nested_frag2.rxtfrag` | depth-first, two deep — frag1 includes frag2 |
| `include_dup_path` (reuses `include_basic_frag.rxtfrag`) | the same resolved real path, two spellings, ONE file's own include lines |

Full detail (why each is shaped the way it is, the `[resolution]`
inline scenario, the corpus-control cost argument): `tests/rxtsource/
CLAUDE.md`'s own "[DD-13b.W23.3a]" section, added in the same change.

### 3.3 Still OWED, and it is box-constrained rather than unbuilt

`make test`, `make test-axes`, `make san`, `make lint`, and `make
mech`'s real (not `VALIDATE_ONLY=1`) `DETECTED` run for S247 — the
SAME box constraint the brief named (`build/battery_20260915_022106`)
held for this lane's entire working period, through both sessions.
Everything in this report was validated with the allowed set: `make
-j4`, `make strict`, `bash tests/rxtsource/run_rxtsource_tests.sh`,
`VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S247`, and
direct `build/pcrec`/`run.sh`/`verify_rxt.py` invocations.

---

## 4. What a fresh agent needs to know

- **Leg A is the oracle.** `build/pcrec --list-source FILE` on any
  fixture is how to check the `include` row's `name`/`value` columns
  directly.
- **`rxt_list_source_cached` (run.sh) / `_rxt_list_source`
  (verify_rxt.py) are the ONE call-site per file for `--list-source`
  in each leg now.** Route any new reader of a file's head through
  them rather than adding a bare call — the two bugs in §1.2 are
  exactly what a bare call reintroduces.
- **A sabotage plant applied to a COPY of `run.sh` outside the repo
  reports nothing meaningful** — `ROOT_DIR` resolves relative to the
  script's own path, so a `/tmp` copy breaks every `tests/lib/*.sh`
  source and every `pcrec` call. Apply in place inside the worktree,
  test, `git diff` to confirm, then restore from a backup.
- **§2's finding governs how any FUTURE include-adjacent check must be
  written.** Leg C cannot open an `include`-bearing file at all, by
  the seam ruling, and that is permanent for this construct — never
  build a `check_refusal_all3`-shaped assertion for it.
- **`--dump` mode's two new stderr lines are the cheap way to ask a
  closure-shape question over the whole corpus.** Reach for
  `bash run.sh --dump DIR 2>&1 >/dev/null` before reaching for a bare
  `bash run.sh DIR`, which pays `test-corpus`'s own compile cost.
