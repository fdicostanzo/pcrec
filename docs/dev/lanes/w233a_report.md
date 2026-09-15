# [DD-13b.W23.3a] — `include`'s harness half (lane w233a)

Branch `lane/w233a`, from `lane/w233` tip `6edfba46`. Step brief:
`docs/design/dd13_format/w23_impl.md` REVISION 1.1 §6.3a; mechanism
§1.10; design of record `format_design.md` 3.4.2 §2.5/§2.11. Three
commits: `4fd013c3` (leg A), `426c974c` (leg B), `da0b80c6` (leg C +
spec hunk).

**STATUS: PARKED, NOT DONE.** Legs A and B are built and verified.
Leg C is built for the ONE thing it can do (discovery subtraction) and
NOT for splice, which turned out to be structurally impossible for it
— a finding, not an omission, explained in §2 below. The three
fixtures, W23-S7's own check code, S247, the census pin's second
number and SW20 are OWED. Read §3 before continuing this lane.

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

**Verified**: `make`/`make strict` clean. Hand fixtures (not committed
— see §3) show resolve / unresolved-refuse / same-file-dup-refuse all
working, each printed and inspected. `tests/rxtsource` 175/0
unchanged, census 210/3936/28943 unchanged (the shipped corpus still
has zero `include` lines, so the new row kind has no population there
— exactly the corpus control §1.10.3 predicts).

### 1.2 Leg B — subtraction, splice, tally, the fourth failure class (§6.3a items 2-5, 7)

`tests/harness/run.sh` gains, in dependency order:

1. **Entry-set subtraction** (§1.10.2 rule 3), run ONCE over the whole
   discovered set before either dispatch branch: a lightweight
   `rxt_head_probe` (factored to match the per-file loop's own test
   exactly), a `pcrec --list-source` call on every head-bearing
   candidate (cached — see §1.4), and a filter that drops any
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
   aggregation): `entry files: N`, `fragments spliced: M`.

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

**Verified by hand, six constructed scenarios** (the shipped corpus
has zero `include` lines and cannot exercise any of this):

| scenario | result |
|---|---|
| flat splice, one fragment | 2 cases, entry files: 1, fragments spliced: 1 |
| nested splice, two deep | 3 cases, entry files: 1, fragments spliced: 2 |
| cross-file duplicate (two DIFFERENT includers reach the same fragment) | refused at the FRAGMENT's own `file:line` (rule 5), entry's own body still runs (1 case), exit 1, `compile_fail_set` +1 |
| `PROCS=2`, two entries, one with a fragment | 3 cases total, entry files: 2, fragments spliced: 1, `parallel: 2 of 2` |
| a fragment that is ALSO independently `.rxt`-discoverable and named on the command line | `"<file>: named, absorbed into <entry>"` printed, entry files: 1, fragments spliced: 1, case counted once |
| the corpus control (any two ordinary corpus files) | entry files: 2, fragments spliced: 0 |

`tests/rxtsource/run_rxtsource_tests.sh`: **175/0** after every leg-B
edit, re-run after each fix. Census **210/3936/28943** unchanged
throughout.

### 1.3 Leg C — discovery subtraction only, and a finding on why (§6.3a item 4, partial)

`verify_rxt.py`'s `discover()` gains the same entry-set subtraction as
leg B: `_rxt_head_probe` (the identical cheap test), `_rxt_list_source`
(subprocess call to `pcrec --list-source`, cached by
`os.path.realpath` — python's own `realpath(3)` binding, so it agrees
with leg A's `name` column by construction, with no `cd`+`pwd`-style
trap to fall into), and a filter identical in shape to leg B's. Prints
the same `"<file>: named, absorbed into <entry>"` line for a bare
argv-named file that gets subtracted.

**Verified**: the same "named, absorbed" smoke fixture leg B used,
run through `discover()` directly — prints the message, returns the
entry only. Ordinary (non-`include`) corpus files unaffected:
`python3 verify_rxt.py tests/base/alternation.rxt tests/base/caseless.rxt`
still reads 82/0. `tests/rxtsource` 175/0, census unchanged, after
this leg's edit too.

**NO SPLICE HERE, and §2 is why.**

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

**What this does NOT affect**: leg A and leg B's OWN mechanisms are
independently verified (§1.1, §1.2) and do not depend on leg C's
participation. The corpus control (§1.10.4's "0 fragments spliced,
entries == CENSUS_FILES") is satisfied by leg C's subtraction alone.

---

## 3. OWED

Everything below is genuinely unbuilt, not merely unvalidated. A fresh
agent resuming this lane should start here.

1. **The three fixtures** (§3.2/§1.10.4): `include_basic.rxtin` +
   `.rxtfrag`, `include_nested.rxtin` + two `.rxtfrag`s,
   `include_dup_path.rxtin` (same resolved path, two spellings, single
   file — leg A already refuses this correctly, verified in §1.1; the
   fixture just needs writing and wiring). Six hand-built equivalents
   exist as scratch files under `/tmp/w233a_smoke*` (not committed,
   not part of this repo, listed in §1.2's table) — they are the
   PROOF the mechanism works, not a substitute for the real fixtures,
   which belong in `tests/rxtsource/fixtures/` with the `.rxtfrag`
   siblings kept OUT of `find tests -name '*.rxt'` per §1.10.4's own
   rule.

2. **W23-S7 itself**, in `tests/rxtsource/run_rxtsource_tests.sh`: the
   population-counted check over the three fixtures — corrected per
   §2 above to a leg-A/leg-B comparison for the closure/splice halves
   (`include_basic`, `include_nested`) and single-leg (`check_refusal`,
   leg A only) for `include_dup_path`'s refusal, matching
   `dup_head_description`'s own established pattern rather than
   `check_refusal_all3`. Plus the corpus-control assertion itself
   (`fragments spliced: 0`, `entry files: 210` over a real `make
   test-rxtsource`-style corpus run) — NOT yet wired as an assertion,
   only manually confirmed via `tests/rxtsource/run_rxtsource_tests.sh`
   printing unrelated totals that happen not to move.

3. **S247** (the sabotage row this step owes, §3.5) — unplanted.
   Highest id on `lane/w233a` at this pin: **S246** is w23_impl's own
   next-numbered row for a different step; re-confirm the highest id
   on `main` before numbering, per the checklist.

4. **The census pin's second number** (§1.10.3 item 3): the script's
   `CENSUS_FILES=210`/etc. pin block needs a companion "entry files
   equals `CENSUS_FILES`, fragments spliced equals 0" assertion added
   explicitly (today this is true by observation, not by an assertion
   that would catch it moving).

5. **SW20** (§1.10.5) — `docs/spec/rxt_format.md`'s "How the harness
   evaluates a block" section (currently `:531-565`-ish, unmoved by
   this lane) needs the cell notion, the entry/fragment counts and the
   RESOLUTION failure class. **MEASURED, still true after this lane's
   own edits**: a grep for `entry file`, `fragments spliced`,
   `resolution failure` across `docs/spec/` still returns zero. This
   is the ONE thing revision 1 of `w23_impl.md` claimed was already
   landed and was not (§1.10.5); it remains not landed.

6. **§6.3a's own acceptance line "S247 turns W23-S7 red on the FIXTURE
   arm and leaves the corpus arm green"** — needs W23-S7 and S247 to
   exist first; not evaluable yet.

Also worth a fresh agent's attention, not blocking: `make test`, `make
test-axes`, `make san`, `make lint` are all OWED — this lane ran under
the SAME box constraint the brief named (`build/battery_20260915_022106`
in flight for essentially this lane's whole working period; it had
progressed to the `axes`/`san` stages by the time this report was
written). Everything above was validated with the allowed set:
`make -j4`, `make strict`, `tests/rxtsource/run_rxtsource_tests.sh`,
and direct `build/pcrec`/`run.sh`/`verify_rxt.py` invocations.

---

## 4. Rulings received

None mid-flight; no ruling request was sent. §2's finding is reported
here rather than escalated, because it does not contradict a Frank
ruling or require one — it is a correction to `w23_impl.md`'s own
prose against the tree, in the same shape several prior W23 lanes'
reports have already recorded for other head-scoped productions.

## 5. What a fresh agent needs to know

- **Leg A is the oracle.** `build/pcrec --list-source FILE` on any
  constructed fixture is how to check the `include` row's `name`/
  `value` columns directly.
- **`rxt_list_source_cached` (run.sh) / `_rxt_list_source`
  (verify_rxt.py) are the ONE call-site per file for `--list-source`
  in each leg now.** Route any new reader of a file's head through
  them rather than adding a bare call — the two bugs in §1.2 are
  exactly what a bare call reintroduces.
- **§2's finding governs how W23-S7 must be written.** Do not build
  `check_refusal_all3`-shaped fixtures for the splice half; leg C
  cannot open an `include`-bearing file at all, by the seam ruling,
  and that is permanent for this construct.
- **The scratch fixtures under `/tmp/w233a_smoke*` are NOT in this
  repo** (session scratchpad discipline) and will not survive this
  session. The exact shapes are in §1.2's table; reconstructing them
  as the real `tests/rxtsource/fixtures/*.rxtin` + `*.rxtfrag` files
  is item 1 of §3.
