# LENS 5 — UNIT-TESTING RECOMMENDATIONS

Lane `lens5unit` (opus, read-only review). Base: `main` @ `7d444f9e`.
Charter: `docs/dev/reviews/code_review_criteria_draft.md` (RATIFIED
2026-09-17), lens 5 (Frank #5) — *"where the suite's answer-level checks
leave internal seams untested (helper-level properties a future refactor
needs as a net): recommend targeted unit surfaces, citing what exists (the
suite is integration-heavy by design — recommendations must not duplicate
oracle coverage)."*

**Nothing under `src/`, `cli/`, `lib/` or `tests/` was written. No `make`,
no build, no suite run.** Every count below is from a grep or from a
committed metric artifact, cited per A5.

---

## 0. THE HEADLINE, AND THE CHARTER'S PREMISE CORRECTED

The charter says *"the repo has no unit tier today, so your FIRST
recommendation is the tier's own shape."*

**The repo has a unit tier. It has ten files in six directories, it runs
inside `make test`, and it has no name, no shared build, and no
membership rule.** Ten C programs `#include "core/internal.h"` and link
`build/libpcrec.a` to assert a property of an internal helper directly,
below any answer:

| file | subject | invoked from |
|---|---|---|
| `tests/codegen/cpset_model_check.c` | `src/core/cpset.c`'s interval algebra vs. a flat-bitset oracle | `run_cpset_structure.sh:553` |
| `tests/parse/branch_count_check.c` | `p_alt`'s branch count vs. an independently-written depth scanner | `run_parse_tests.sh:55` |
| `tests/mrl/cwmax_check.c` | `pcrec_cwmin`/`cwmax` vs. the corpus's own oracle spans | `run_mrl_tests.sh:522` |
| `tests/backrefs/fold_agreement_check.c` | `pcrec_ascii_fold` vs. an emitted artifact's caseless compare, all 65,536 ordered pairs | `run_backref_diff.sh:654` |
| `tests/backrefs/fold_agreement_utf8_check.c` | the same seam under `utf8` | `run_backref_diff.sh:682` |
| `tests/utf8/startbnd_backend_check.c` | the encoding backend's start-boundary rule | `run_startbnd_diff.sh:415` |
| `tests/registry/registry_check.c` | 225 registry-row invariants | `run_registry_tests.sh:39` |
| `tests/registry/definitions_check.c` | the definitions table's containment rules | `run_definitions_tests.sh:87` |
| `tests/registry/pcre2_check.c` | PC-3, the registry against libpcre2 | `run_registry_tests.sh:187` |
| `tests/registry/definitions_oracle_gen.c` | the definitions oracle generator | `run_definitions_oracle.sh` |

That changes the first recommendation from *invent a tier* to *name the
tier you have, give it one build, and give it a membership rule* — which
is both cheaper and consistent with the tree's own instinct against
parallel mechanisms (memory `pcrec-general-mechanisms-not-special-cases`;
D75 addendum). Minting a `tests/unit/` beside these ten would be the
second mechanism for the thing that already exists.

**The second headline is that the tier's missing build IS a live
coverage hole, not a tidiness complaint.** The ten build sites carry
**four different flag policies**, and two of the scripts holding them are
absent from `tests/lib/san_scripts.txt`:

- `run_cpset_structure.sh:553` compiles with `-O1 -std=gnu11 -Wall
  -Wextra -Werror` and **mentions `SANFLAGS` nowhere in the file**; the
  script is not in `san_scripts.txt` (35 entries, checked at
  `7d444f9e`). So **`cpset_model_check.c` — the tree's best unit check,
  whose whole stated argument is that it reaches paths the corpus cannot
  — has never been built under a sanitizer.** Its randomized walk over
  `pcrec_cpset_add`/`remove`/`complement` is precisely where an
  out-of-bounds interval write would live, and it is the one
  cpset-exercising binary ASan never sees.
- `run_mrl_tests.sh:522` reads `${SANFLAGS:-}` and the script is also
  absent from `san_scripts.txt`, so its threading is dead: `cwmax_check.c`
  is never instrumented either. (`run_definitions_tests.sh` reads
  `$SANFLAGS` and IS reached — `run_registry_tests.sh:592` invokes it and
  that script is in the manifest, so the env var propagates. Checked, not
  assumed.)
- `run_parse_tests.sh` / `run_registry_tests.sh` / `run_definitions_tests.sh`
  use `-O1 -g … $SANFLAGS` with **no `-Werror`**; `run_cpset_structure.sh`
  and `run_startbnd_diff.sh` use `-Werror` with no `-g`;
  `run_backref_diff.sh` uses `$GENCFLAGS`, the *generated-code* flag set,
  for a check that compiles *library* source.

This is [TT-9]'s own lesson recurring one tier over. `san_scripts.txt`'s
header says a manifest exists because two copies of a list *"silently
disagree"* — and the tier's build flags are ten copies of a list with no
manifest at all.

---

## R0 — THE TIER'S SHAPE (the charter's first ask)

**Severity: MAINTAINABILITY (with one CORRECTNESS-RISK consequence, the
cpset/san gap). Effort: MECHANICAL. Blast radius: 6 scripts, 1 manifest,
1 new `tests/lib/` helper; 0 sabotage anchors on any build block
(verified by grep over `tests/mech/sabotages/` for each script name); 0
emitted bytes; no abi event.**

**Evidence (A5):** `function_census.tsv` supplies the subject rows cited
throughout (`src/core/cpset.c:cpset_grow` 72-81, `src/core/sb.c:sb_grow`
8-31, `src/core/arena.c:arena_alloc` 8-33, `src/opt/mrl.c:mrl_sat_add`
93-97, `src/gen/emit_vm.c:vm_fadd` 3136-3140,
`src/opt/callgraph.c:cg_sat_add` 458-463). The ten-file tier population
and the four flag policies are direct greps, stated above.

### R0.1 — one build function, in `tests/lib/`

```sh
# tests/lib/unit_cc.sh — the ONE way an internal-property check is built.
#   unit_build <outbin> <src.c> [extra sources/flags…]
# Resolves CC via cc_resolve.sh, applies -Ilib -Isrc, threads $SANFLAGS
# and $LIBPCREC (the SAN-1 overrides), links "$LIBPCREC", and hard-fails
# naming the file on a build error.
```

Every one of the ten sites becomes one call. The three properties the
helper makes structural rather than remembered: `$SANFLAGS` cannot be
forgotten, `$LIBPCREC` cannot be forgotten (which is what makes the san
target instrument the *library* axis and not just the check), and the
warning policy is one decision instead of four.

**The warning policy is a real question and I recommend `-Werror`
everywhere**, on `docs/testing.md`'s own K28 record: `-Werror` on the
generated-code compile path found a maybe-uninitialized read no answer
check could see, and `-Werror` stopping at the first report is why that
entry *"named ONE site and there were THREE."* FIVE of the build sites
read here carry no `-Werror` at all (`run_parse_tests.sh`,
`run_mrl_tests.sh`, `run_registry_tests.sh` at both `:39` and `:187`,
`run_definitions_tests.sh`); the two `run_backref_diff.sh` sites inherit
it only via `$GENCFLAGS`, which is a different variable with a different
owner. This does **not** contradict R5-Q1 (`-Werror` is
deliberately not `make`'s default so a stranger's newer gcc cannot fail
their build): these are *test* compiles, already gated behind a suite
whose failure the stranger is expected to read, and `GENCFLAGS`'s own
`-O1 -Werror` is the shipped precedent for exactly that distinction.

### R0.2 — membership: add the two absent scripts to `san_scripts.txt`

`tests/codegen/run_cpset_structure.sh` and `tests/mrl/run_mrl_tests.sh`.
This is the CORRECTNESS-RISK half of R0 and it is two lines.

**Failing-direction story** (learnings §3 — an invariant with no
population and no sabotage is a sentence): the addition is validated by
an off-by-one in `cpset_grow`'s `memcpy` length
(`src/core/cpset.c:78-79`, `memcpy(iv, s->iv, (size_t)s->n * sizeof *iv)`
→ `(s->n + 1)`) in a scratch tree: the model check's *answers* stay
correct (it reads one stale interval past the end and the walk usually
overwrites it), ASan reports it, and **today ASan is not looking.** Run
that scratch build before and after the manifest edit; if the "before"
run is silent the finding is confirmed as filed.

### R0.3 — a name and a home for NEW checks: `tests/core/`, not `tests/unit/`

The ten existing files stay where they are. They are co-located with the
suite that owns their subject, which is this tree's directory convention
(`tests/mrl/` owns MRL, `tests/backrefs/` owns the fold), and moving
them would stale `run_cpset_structure.sh`'s and `run_backref_diff.sh`'s
own text needles for zero gain.

What has no home is a check on a `src/core/` helper that belongs to no
feature — `sb.c`, `arena.c`, and the shared arithmetic and vector
primitives the refactor waves will mint. **Recommend one new directory,
`tests/core/`, named after its subject the way every other test
directory is**, with its own `CLAUDE.md`, its own `run_core_tests.sh`
driver built on `unit_cc.sh`, one `make test-core` section wrapper, and
`san_scripts.txt` membership from the first commit. A generic
`tests/unit/` would attract everything and would be a second home for
checks that already have one; `tests/core/` cannot, because its name
says what it holds.

### R0.4 — the cost budget

The reason this tier is affordable at all is structural and worth
stating as the rule rather than as a number. [TT-4]/[TT-4M] measured
that `make test`'s cost is gcc invocations plus process spawns — 255.79
gcc-core-seconds in `corpus` alone, and a per-binary first-launch cost on
darwin that batching collapsed 11.79x. **A unit check is ONE gcc
invocation and ONE process spawn, for an arbitrary number of assertions.**

So the budget is a shape, not a stopwatch:

1. **One binary per SUBJECT, not per assertion.** `cpset_model_check.c`
   holds a randomized walk plus seven written-out edge cases in one
   program; that is the pattern.
2. **No check in this tier may invoke `pcrec` or `gcc` per case.** A
   check that compiles a pattern per case is a differential driver and
   belongs in the suite that owns that feature, under D45's gen-timeout
   budgets.
3. **No check in this tier may read the `.rxt` corpus** — with
   `cwmax_check.c` as the deliberate, already-shipped exception, because
   its subject genuinely is "the analysis against every pattern we have."
   A new corpus-sweeping check is not a unit check.
4. **Ceiling: the whole tier's marginal wall time stays under the noise
   floor of one existing section.** The measurement that fixes the number
   is one `make test-core` run on a quiet box against
   `docs/testing.md`'s "Measured per-section runtimes" table; **this lane
   did not take it** and names it here rather than guessing (D77).

The deterministic-PRNG rule is also part of the budget and already
shipped: `cpset_model_check.c` seeds to a constant *"so a failure is
reproducible from the printed iteration number."* A unit check that
needs a retry to reproduce costs more than it saves.

### R0.5 — A1: the one ruled record that bears on this lens, and it is not a bar

**`docs/dev/decisions.md:4602` is the tree's only ruling on a unit test,
and it is a ruling against a specific one, not against the tier.**
[M4.7a]'s first pass built SR-8's lowering-time engine-capability
consultation *"unit-tested with a hand-built Ctx standing in for a
producer that does not exist"*, and the manager reverted it:

> *"the hand-built-Ctx test is a control sharing a source with what it
> controls: it proves the plumbing runs, not that a real producer's
> contract … matches what was guessed at sample size zero."*

That is binding on this lens and every recommendation below is written
to it. The distinction it draws is between two different things:

- **A unit test whose INPUT is fabricated to stand in for a caller that
  does not exist** — refuted, permanently. Sample size zero.
- **A unit test whose input is the helper's OWN total input domain, and
  whose oracle shares no source with the helper** — which is what
  `cpset_model_check.c` (4,096-point flat-array oracle, no intervals),
  `branch_count_check.c` (a different algorithm, cross-checked against
  libpcre2's two thresholds) and `fold_agreement_check.c` (all 65,536
  ordered pairs, one side read out of an emitted artifact) already are,
  and all three shipped after that D-row.

**Every recommendation below is required to state which of the two it
is.** A recommendation that cannot name an oracle sharing no source with
its subject is not filed.

No other ruling in `decisions.md`, `docs/testing.md` or `APPROACH.md`
bears on unit tiers (searched: `unit test`, `unit-test`, `unit tier`,
`tests/unit` across all four plus `docs/spec/`; one hit, the row above).

---

## R1 — ALLOCATION-FAILURE INJECTION (lens 8's F6(d), judged)

**Severity: CORRECTNESS-RISK (it is the only instrument that finds an F1
directly). Effort: LOCAL — and this is the judgement the brief asked
for. Blast radius: 1 new build tree, 1 new check, 0 bytes under `src/`,
0 sabotage anchors staled, no abi event.**

**Evidence (A5):** lens 8's F1 and F6
(`worktrees/lens8err/docs/dev/reviews/lens_reports/lens8_error_cleanup.md`),
cited rather than re-derived: 38 raw allocation sites in 10 files; zero
sabotage rows on `arena.c`/`sb.c`/`compile.c`'s attachment block
(re-verified here by grep over all 261 rows in `tests/mech/sabotages/` —
`src/core/sb.c` 0, `src/core/arena.c` 0, `src/core/cpset.c` 0,
`src/opt/minimize.c` 0); the only positive control is
`tests/resource/run_resource_tests.sh` section 2, skipped on darwin.
Census rows `src/core/arena.c:arena_alloc` 8-33 (21 code lines) and
`src/core/sb.c:sb_grow` 8-31 (15).

### The judgement

**Lens 8 files the injector as a DESIGN-EVENT deferred under D77, and I
think that is one tier too heavy — because there is a spelling that
needs zero edits under `src/`.** D77's bar is a measured need; the
measured need is already on the record (F1 is live, reachable on any VM
compile taking the cursor rung, and nothing in the tree could have seen
it). What made the injector look like a design event is the assumption
that it requires an allocation hook compiled into the library. It does
not.

The tree already has the mechanism: `BUILD_DIR` (Makefile:19-24)
parameterizes every output location *"so the sanitizer targets can build
a SEPARATE tree without ever touching `build/`"*, and `CFLAGS` flows into
`ALLFLAGS` (Makefile:17). So:

```make
ALLOC_DIR := build-alloc
alloc:
	$(MAKE) BUILD_DIR=$(ALLOC_DIR) \
	        CFLAGS="-O1 -g -include $(CURDIR)/tests/core/alloc_inject.h" all
	bash tests/core/run_alloc_tests.sh
```

`tests/core/alloc_inject.h` includes `<stdlib.h>` and `<string.h>`
**first** — `-include` puts it ahead of everything in the translation
unit, so the real declarations are processed before any macro exists,
which is the detail that otherwise costs an implementer an afternoon —
and then defines `malloc`/`calloc`/`realloc`/`strdup` as function-like
macros onto `pcrec_inject_*`. The injector's counter and its definitions
live in the check driver, so the library archive carries undefined
symbols resolved at link, exactly as `fold_agreement_check.c` already
resolves against a generated `gen.c`.

Nothing under `src/`, `cli/` or `lib/` is edited. `build/` is untouched.
That is not a design event; it is the `make ubsan` shape, one axis over.

### The property, and why it needs a unit surface

The claim under audit is `src/core/CLAUDE.md`'s own rule — *"pcrec is a
LIBRARY, and aborting kills the CALLER's process"* — universally
quantified over allocation sites. The check:

> For every N in 1..K, a build in which the **Nth** allocation returns
> NULL must answer `pcrec_compile` with a diagnosed error, never
> `abort()`, never a signal, never success; and the arena must be freed.

**Why answer-level coverage cannot see it, precisely.** The closest
existing section is `tests/resource/run_resource_tests.sh` section 2,
and it is blind for three independent reasons lens 8 enumerates: it is
skipped on darwin (`:705-706`), its verdict arm accepts *"out of memory |
too complex | too large"* so a budget refusal scores as an allocation
failure (`:659`), and — the reason that survives even a full repair —
**an `RLIMIT_AS` ceiling fails whichever allocation happens to cross the
line, and nothing steers it to a chosen site.** Its header's claim that
four patterns put the failure in four named allocators (`:679-683`) is
asserted, not measured; no cell verifies which site failed. A counter is
a steering wheel; a limit is a wall.

**Sharing no source with the subject (R0.5's bar).** The injector knows
nothing about pcrec: it counts calls and returns NULL on the Nth. The
subject is the whole library's failure discipline. The oracle is the
process's own exit status and `pcrec_error`'s contents. There is no
fabricated caller — the input is a real pattern compiled by the real
entry point.

**Failing-direction story.** Three, in increasing strength:

1. Revert one `ctx_nomem(cx)` to `abort()` in `arena.c:22` in a scratch
   tree; the check must red at the N that reaches it. This is the
   sabotage lens 8's F6(a) says K7's own fix note describes having run
   by hand and never committed — the injector is what makes it a
   committed row (`SAB_FILE="src/core/arena.c"`, which today has none).
2. Delete `cx.job->csb.cx = &cx;` from `compile.c:761`; the check must
   red on a pattern reaching `csb`.
3. **The acceptance case: it must red on F1 unrepaired.** Compile
   `[a-z]{2,10}` (the VM cursor rung, lens 8's reaching sequence) and
   sweep N; with `Job.scr_test.cx` still NULL the process aborts. If the
   check does not red there, it has not been built to find the thing that
   justified it.

### Staging — and lens 8's ordering is right

R1 is the second wave, not the first. F6(a) (one sabotage row) and F6(b)
(split the verdict arm so `out of memory` is its own outcome) are two
small edits that make the class detectable at all. **F6(c) belongs to
this lens and is the one I would add**: the stale six-file list in
`run_resource_tests.sh`'s header should be replaced by a grep-derived
census of raw allocation sites and their failure routes, asserted against
a pinned count. That is not a unit test; it is the same shape as
`san_scripts.txt` — the *list* is an input someone chose (learnings §3,
the reference-build-by-glob rule), and a hand-written one goes stale
exactly the way `dialimpl`'s §5.3a manifest and `w23implfix`'s
five-token withdrawal check did. It would have failed the day
`emit_dfa.c` and `scr_test` arrived.

### The residual I will not hide

`K` is unbounded in principle and a full sweep is O(allocations)
compiles. The tier budget (R0.4 rule 2) forbids a per-case `pcrec` call,
so this check is a deliberate, named exception: it is one binary that
calls `pcrec_compile` in-process K times. **The measurement that sizes
it** — the distribution of allocation counts per compile over a handful
of representative patterns — has not been taken. Until it is, the honest
scope is a fixed small K over a fixed witness set (one DFA pattern, one
VM cursor-rung pattern, one `\p{L}` under `-e utf8`, one `--source`
target), not an exhaustive sweep.

---

## R2 — THE SATURATING-ARITHMETIC AGREEMENT (lens 1's X3)

**Severity: CORRECTNESS-RISK. Effort: MECHANICAL. Blast radius: 1 new
check file, 0 src bytes, 0 anchors staled (the check is additive; X3's
own refactor stales S58/S59/S-U4, which is X3's cost, not this
check's).**

**Evidence (A5):** `clone_candidates.tsv` group 32 (`vm_fmul`,
`cg_sat_mul`, `mrl_sat_mul`; two members at `group_frac` 1.000);
`function_census.tsv` rows `src/opt/mrl.c:mrl_sat_add` 93-97 /
`mrl_sat_mul` 99-104, `src/gen/emit_vm.c:vm_fadd` 3136-3140 / `vm_fmul`
3143-3148, `src/opt/callgraph.c:cg_sat_add` 458-463 / `cg_sat_mul`
465-471. Lens 1's X3.

**This is the sharpest unit-checkable property in the tree and the brief
is right to call it out.** `src/opt/CLAUDE.md`'s `mrl.c` entry states the
requirement as a correctness fact —

> *"Arithmetic saturates at `PCREC_MINW_MAX` … **shared with the
> emitter's accumulator so a long concatenation of saturated subtrees
> cannot overflow past the ceiling that exists to prevent it**. A wrapped
> product is not merely wrong, it is wrong in the UNSOUND direction
> whenever it lands on a small positive value."*

— and `src/gen/emit_vm.c:3131-3135` restates it from the other side
(*"the accumulator has to hold the same ceiling or a long enough
concatenation of saturated subtrees could still overflow"*). **Two
sources, one requirement, and nothing checks the agreement.** Today it
holds because two authors happened to type the same five lines.

`src/opt/mrl.c:91` is `#define MRL_MINW_MAX PCREC_MINW_MAX`, so after
macro expansion `mrl_sat_add` and `vm_fadd` are the *same function* —
which means the agreement is checkable by value over a shared input set
with no modelling at all.

### The check

`tests/core/sat_arith_check.c`: the three add implementations and the
three mul implementations evaluated over one input set, asserting
pairwise equality within each ceiling family, plus the three
*algebraic laws* the callers rely on and the implementations do not
state:

- **Monotone**: `a ≤ a'` ⇒ `sat_add(a,b) ≤ sat_add(a',b)`. This is what
  makes saturation an under-estimate and therefore safe
  (`emit_vm.c:3134`: *"Under-estimating is the safe direction and
  saturation is an under-estimate"*).
- **Capped**: the result never exceeds the ceiling and never goes
  negative. A wrap is a negative or a small positive — the unsound
  direction `src/opt/CLAUDE.md` names.
- **Absorbing**: `sat_*(cap, b) == cap` for every `b ≥ 0`.

The input set is boundaries, not a random walk: `{0, 1, 2, cap/2−1,
cap/2, cap/2+1, cap−2, cap−1, cap, cap+1, LLONG_MAX/2, LLONG_MAX}` × the
same, plus the negatives the `a <= 0 || b <= 0` guards exist for. ~600
pairs per operation; one binary, microseconds.

**A2 — the abstraction this check is the net for.** X3 proposes
`pcrec_sat_add`/`pcrec_sat_mul` in `core/internal.h` taking the ceiling
as a parameter. The check is written **against today's three
implementations first**, goes green, and then is the instrument that says
the unification changed nothing. That ordering matters: written after the
refactor it can only compare one implementation with itself.

**X3's one open precondition is exactly what this check answers.** Lens 1
flags `cg_sat_add`'s extra leading `if (a >= CG_EXP_INF || b >=
CG_EXP_INF) return CG_EXP_INF;`, which the `mrl`/`vm` pair lacks, and
says *"it appears redundant — but 'appears redundant' is how this project
loses things."* The check decides it by evaluation rather than by
reading: run `cg_sat_add` with and without the guard over the input set;
if the outputs are identical on all ~600 pairs the guard is redundant on
that domain, and if they are not, the differing pair is the witness that
says the shared helper must take the absorbing form.

**Failing-direction story.** Four sabotages, each targeting one of the
four things that can differ: (a) change `MRL_MINW_MAX` to `1LL << 39` —
the cross-family equality reds; (b) delete `mrl_sat_add`'s clamp — the
capped law reds on `(cap, 1)`; (c) change `mrl_sat_mul`'s `a > cap / b`
to `a >= cap / b` — the equality reds on a boundary pair and no other;
(d) flip `a <= 0` to `a < 0` — reds on `(0, k)`. **Sabotage (c) is the
one that matters**, because it is the mutation a careless unification
would actually make, and it is invisible to every answer check: it
under-estimates by one, and under-estimating is the safe direction, so
no pattern gives a wrong answer — it only stops pruning somewhere. Which
is the definition of a seam an answer-level suite cannot reach.

**Why answer-level coverage cannot see it.** `tests/mrl/run_mrl_tests.sh`
is the closest section, and `docs/testing.md` states precisely what it
asserts: MRL *"is a bound emitted ON whichever rung a quantifier already
took"*, and a `-fno-length-prune` build is **byte-identical** for 701 of
944 compilable patterns. So MRL's own answer identity is its acceptance,
and a bound that is merely *looser than it could be* passes every cell.
The arithmetic can be wrong in the under-estimating direction across the
entire corpus with `make test` green. Its over-estimating direction is
caught — by answers — which is why this check is aimed at the half that
is not.

**A rider for lens 3, flagged here because this seam surfaced it and it
is sharper than lens 1's version.** `src/core/limits.def:358` declares
`PCREC_MINW_MAX` as `(1LL << 40)` and its own `where` text names
**`src/opt/callgraph.c`** as the site — and `callgraph.c:456` does not
use it, it re-declares `#define CG_EXP_INF ((long long)1 << 40)`. The
ruled central-config row points at a file that carries an independent
copy of its value. Lens 3's finding; not mine to file.

---

## R3 — THE ARENA VECTOR PRIMITIVE, SPECIFIED BEFORE WAVE 1 BUILDS IT

**Severity: MAINTAINABILITY (CORRECTNESS-RISK if the primitive ships
unchecked). Effort: MECHANICAL. Blast radius: 1 new check; the
primitive's own wave carries S201's re-aim (X5), not this check.**

**Evidence (A5):** `clone_candidates.tsv` groups 3 and 10 (four members
at `group_frac` 1.000); lens 1's X5 (10 sites), lens 2's rank 3 (7
sites). **The census shows more than either lens named** —
`function_census.tsv` carries at least thirteen rows of this shape:
`row_push` 615-631, `prov_push` 1370-1382, `variant_push` 1384-1396,
`case_push` 1398-1410, `aux_push` 1412-1424, `seen_add` 3209-3220 (all
`src/parse/rxt_source.c`), `cpset_grow` 72-81 (`src/core/cpset.c`),
`ds_add` 376-387 (`src/opt/atomic.c`), `u8_push_branch` 202-212
(`src/opt/lower_enc.c`), `libdir_push` 362-373 (`cli/main.c`),
**`cont_push` 444-456 (`src/ir/dfa.c`)**, **`patch_push` 103-114
(`src/ir/nfa.c`)** and **`vm_push_at` 2964-2974 (`src/gen/emit_vm.c`)`.
The last three are in neither lens's list; the synthesis should count
thirteen, not ten or seven.

The brief's instruction is the point of this item: **the kit primitives
about to be built need their unit surfaces specified BEFORE wave 1
builds them.** For `pcrec_arena_vec_push` the surface is four properties,
all of them total over a small domain, none of them visible to any
answer:

1. **Content preservation across growth.** Push `k` elements for
   `k = 0..4·seed`, each stamped with its own index; after every push,
   all `k` previous elements still read back their own index. This is
   the `memcpy`-length property and it is the one an off-by-one gets
   wrong. `cpset_grow`'s `memcpy(iv, s->iv, (size_t)s->n * sizeof *iv)`
   is the shape; `row_push`'s `if (src->nrows) memcpy(...)` is the same
   shape with the zero guard the others omit.
2. **The new element is zeroed.** Every caller relies on it
   (`row_push:624` `memset(r, 0, sizeof *r)` then sets three fields and
   leaves the rest; `arena_alloc` already zeroes, which is *why* the
   copy-into-a-fresh-block strategy works). A primitive that returns the
   old block's bytes when capacity was already sufficient is a silently
   wrong reuse.
3. **Capacity monotone, and the seed honoured.** `cap` never shrinks;
   the first allocation is exactly `seed`. Six of the thirteen sites
   seed at 8, 16 or 32 today, so `seed` is a parameter and a check that
   fixes it at one value tests one caller.
4. **Alignment.** The returned pointer is suitably aligned for `elem`.
   `arena_alloc` rounds to 16 (`arena.c:10`), so this holds today — and
   it holds *because of a line in a different file*, which is exactly the
   kind of fact a refactor drops.

**Sharing no source with the subject.** The oracle is a plain `int`
array grown by `realloc` in the check itself — `cpset_model_check.c`'s
own move, and its stated reason: *"The oracle is a flat byte array, which
is the point: it has no intervals, no merging, no ordering and no
invariant, so it cannot fail the same way the subject does."*

**Failing-direction story.** (a) `n` → `n − 1` in the copy: property 1
reds at the first growth boundary and nowhere else. (b) Drop the
`memset`: property 2 reds — **and it reds only when the block is
REUSED**, so the check must push past a growth boundary and then push
again, which is the case a naive three-element test misses. (c) `cap *
2` → `cap + 1`: nothing reds, and that is correct — it is a performance
change, not a correctness one, and the check should not pretend
otherwise.

**A1.** X5 cites `src/parse/rxt_source.c:1364-1368`, an author's recorded
choice to write four copies *"so there is one pattern for 'a section
array that grows' rather than four independently-invented ones."* This
recommendation does not contradict it — it is a check on whatever
primitive wave 1 produces, and if wave 1 declines to build one the check
has no subject and is not written. **Do not write this check against the
thirteen copies.** Thirteen near-identical checks for thirteen
near-identical functions is the perversion lens 11 warns about, and it
is why this item is filed as a *specification for a primitive* rather
than as coverage for today's tree.

**`cli/main.c:libdir_push` is out of scope** and stays out: it `realloc`s
rather than arena-allocating, and `cli/main.c:1231-1246` builds a whole
stated invariant on its being the CLI's only allocating option (lens 8's
F2/H10).

---

## R4 — THE TEXT KIT'S PRIMITIVES, SPECIFIED BEFORE WAVE 1 BUILDS THEM

**Severity: CORRECTNESS-RISK for `txt_f` (K38 is the recorded miscompile
of exactly its absence); MAINTAINABILITY for the rest. Effort: LOCAL.
Blast radius: 1 new check; the kit's own migration carries its 24 anchor
re-aims (lens 2 §4.1), not this check.**

**Evidence (A5):** lens 2 §2.2's API sketch, §1.0's grep census (105
`snprintf`-into-`char[N]` sites; 652 `%s_` substitutions; five row
emitters, three with no escaping), and `src/core/limits.h:50-70` (K38).

This is the brief's explicit second ask, and it is the item with the
best ratio in the report, for one reason: **`txt_f`'s defining property
is that it cannot truncate, and truncation is invisible to every check
in the tree that runs at the default prefix.** K38's own entry says so —
a 60-character `-p` prefix met buffers sized for `"rx"` and produced
uncompilable C, *"invisible to every corpus artifact because they all
use the 2-char 'rx' prefix."*

### R4.1 — `txt_f` (lens 2's item 2): the no-truncation property

`tests/core/txt_check.c`, over a length ladder that straddles every
boundary the 49 hand-sized buffers use (lens 2 counts `emit_vm.c` 41,
`emit_dfa.c` 8) and `PCREC_MAX_EMIT_NAME_LEN`:

> For every `n` in a ladder crossing 15/16/17, 31/32/33, 47/48/49,
> 159/160/161 and `PCREC_MAX_EMIT_NAME_LEN` ± 1, `strlen(txt_f(a, "%s",
> s_n)) == n` and the bytes are `s_n` exactly.

Total over the property's own boundary set, oracle-free (`strlen` and
`memcmp` against the input). No fabricated caller: the input is a
string, which is what the primitive takes.

**Why answer-level coverage cannot see it.** The closest existing check
is `tests/cli/run_cli_tests.sh` case 3, K38's own reproduction, and it
covers *one* prefix length against *the sites that existed when it was
written*. Lens 2's step-3 acceptance number is "provably clean at every
one of the 49 hand-sized sites" — and the honest way to get there is not
49 CLI cases but one primitive with one check plus the migration. This
check is what makes lens 2's §2.4 step 3 acceptance statement
mechanically true rather than argued.

**Failing-direction story.** Implement `txt_f` the wrong way on purpose —
a fixed `char buf[160]` + `snprintf` + `arena_strdup` — and the ladder
reds at exactly 160, silently passing everything below. That transcript
is worth committing beside the check, because it is the shape 105 sites
in the tree have today.

### R4.2 — `txt_field`/`txt_row` (lens 2's item 4): two properties, one of them free

**Property A (structural, oracle-free, total over 256 bytes):** no byte
in `txt_field`'s output is TAB, LF, CR or `< 0x20`, except as part of a
backslash escape. Sweep all 256 single-byte inputs plus adversarial
strings (a lone trailing backslash; `\t` adjacent to a literal `\`;
`\x7f`). This is the property the format needs and it needs no second
implementation to state.

**Property B (injectivity):** distinct inputs produce distinct fields.
This is what *"the columns cannot shift"* actually rests on, and A alone
does not imply it — an escaper that mapped both `\t` and the two-byte
string `\` `t` onto `\t` satisfies A and corrupts. Check it by decoding
with a ten-line unescaper written in the check as a **deliberately
different algorithm** (`branch_count_check.c`'s own rule: *"Different
algorithm, different code, different failure modes. It is not a
transcription"*), and asserting `decode(encode(s)) == s` over the same
sweep.

**Why answer-level coverage cannot see it.** `tests/rxtsource/
run_rxtsource_tests.sh` asserts field COUNTS per dump row — and
`w23impl_report.md` recorded that same assertion going stale with its
failure message *"naming a TAB in a field as the only possible cause."*
A field-count check sees a row that split; it cannot see a row that
should have split and did not, and it cannot see two distinct values
that collided. Both are what B is for. And the corruption is already
diagnosed in the tree without a check:
`src/parse/rxt_source.c:3735-3742` records three corpus blocks carrying
a literal TAB, *"a three-row-in-3,265 corruption, which is the size of
finding a summary swallows."*

**The measurement lens 2 names first is still the right first step and
this check does not replace it**: does any string reachable by
`axes_dump.c`, `limits_dump.c` or `schema_dump.c` contain a tab, newline
or control byte today? If the population is zero the migration is
byte-neutral insurance; if it is non-zero it is a bug fix. **Neither
lens took it.** The unit check is what stops the population from
becoming non-zero silently afterwards — and the two are complementary,
because the check cannot see whether anyone is currently corrupting
anything.

### R4.3 — `txt_join` (lens 2's item 5): the over-long policy is the property

Lens 2's M8 finds five implementations with **three different and
undocumented over-long behaviours**, one of which
(`src/parse/enabled.c:180`) `continue`s past a too-long name and keeps
appending shorter later ones — *"an out-of-order partial list, not a
prefix."* The unit surface is one sentence: whatever policy the kit
picks, `txt_join` produces either the complete list or a documented
prefix of it, never a reordered subset. Check over a name list whose
lengths straddle the bound in both orders (long-then-short and
short-then-long) — **the second ordering is the only one that catches
`enabled.c`'s shape**, which is why "test it with one long name" would
not.

---

## R5 — THE AST TRAVERSAL (lens 1's X1): the net X1 needs

**Severity: CORRECTNESS-RISK (the discipline it checks is a segfault and
a non-terminating compile). Effort: LOCAL. Blast radius: 1 new check;
X1's own extraction carries S91/S97/S104/S158/S159/S174's re-aims, not
this check.**

**Evidence (A5):** `clone_candidates.tsv` group 1 (36 members); lens 1's
direct census of 75 hand-written spine sites in 9 files and 48
exhaustive `AKind` switches in 16 files; `function_census.tsv`
`src/opt/callgraph.c:cg_walk` 121-147 and
`src/opt/postresolve.c:pr_walk` 92-122, both `group_frac` 1.000 (X2's
pilot pair).

Lens 1's second headline is that *"the duplicated thing is not text, it
is a safety discipline … correct because 75 authors each remembered, not
because anything makes forgetting impossible."* X1 makes forgetting
impossible by moving the traversal into one function — and **a
discipline that lives in one function is a discipline a unit check can
assert**, which it categorically was not while it lived in 75 copies.

Two properties, both about the traversal and neither about any
predicate's verdict:

1. **Bounded C-stack depth on a long spine.** Build (via
   `pcrec_parse`, not by hand — the input is a real pattern) a pattern
   whose AST is a left-nested `A_CAT` spine of a few thousand elements,
   walk it, and assert the walk's own recursion depth stays O(pattern
   nesting depth) rather than O(spine length). `src/opt/mrl.c:108-112`
   states the rule the check would pin: *"`clo_visit` was not a problem
   because it recursed; it was a problem because it recursed Θ(d²) …
   Two shapes here are NOT bounded by paren depth and are therefore
   walked ITERATIVELY."*
2. **The back edge is never followed.** Walk `(a(?1))` under `--features
   recursion` and assert the walk terminates and visits
   `u.call.body`'s nodes zero times. Today this is
   `subroutines_design.md` §4.4's rule re-argued *"in a fresh comment
   block at nearly every one of"* the 75 sites.

**Why answer-level coverage cannot see either.** Property 1's failure is
a **stack overflow**, which a test suite observes as a signal with no
attribution — the corpus would tell you "something crashed", not "the
shared walk recursed on the spine", and only on a pattern long enough to
exhaust the stack, which the corpus's own length distribution may not
contain. Property 2's failure is **non-termination**, which every
existing check observes as the D45 budget or the harness `timeout`
firing — indistinguishable from any other slow compile. Both are
properties of the *traversal*, and the suite's whole vocabulary is
answers.

**Sharing no source with the subject.** Property 1's oracle is a depth
counter in the check's own classifier callback — instrumentation, not a
second walk. Property 2's oracle is a visit tally keyed by node pointer,
again in the check. Neither re-implements the traversal, which is the
trap: a check that walks the AST itself to decide what the walk should
have visited is a control sharing a source with what it controls.

**Failing-direction story.** (a) Change the shared spine loop to recurse
into `->l`: property 1 reds (as an assertion, before the stack dies —
which is the whole reason to count depth rather than to observe a
crash). (b) Add an `AW_DESCEND` arm for `A_CALL` that follows
`u.call.body`: property 2 reds on `(a(?1))` by tally, not by timeout.

**Do this with X2, not with X1.** Lens 1 stages `cg_walk`/`pr_walk`
(edge-policy identical, `group_frac` 1.000 both) as the zero-risk pilot
that de-risks X1. The check should be written against **that** merged
`pcrec_ast_visit` first, where its subject is 27 lines and its blast
radius is two files — and then inherited by `pcrec_ast_walk` when X1
lands. Writing it against today's eleven separate walks would mean
eleven checks, which is the wrong shape for the same reason R3 is.

**A1, and it is the one X1 has to answer anyway.**
`src/opt/atomic.c:28-36` rules that none of the seven switches in that
file carries a `default:`, because *"a node kind added after this file is
written must be a COMPILE ERROR at each of them."* X1's proposed shape
preserves it exactly — eleven exhaustive switches stay eleven exhaustive
switches, returning a verdict instead of performing the descent — and
**this check does not touch that axis at all.** It checks the driver, not
the classifiers. That separation is worth stating because a reader could
reasonably fear the opposite: that a unit check on the walk would want
to enumerate kinds, and thereby become the twelfth place a new `AKind`
has to be added. It must not, and the way it must not is by taking its
classifier from the test and never enumerating a kind it does not
itself construct.

---

## R6 — THE DFA TABLE EMITTER'S WRAPPING BOUNDARIES (lens 1's X7) — LOW, AND CONDITIONAL

**Severity: POLISH. Effort: MECHANICAL. Blast radius: 1 new check.
CONDITIONAL on a measurement this lane did not take.**

**Evidence (A5):** `clone_candidates.tsv` group 11 (5 members,
`group_frac` 0.478-0.750) plus `emit_stay_table` from group 29;
`function_census.tsv` `emit_tr_table` 2610-2623, `emit_eol_table`
2727-2737, `emit_end_table` 2742-2752, `emit_acc_cls_table` 2906-2919,
`emit_seed_table` 2946-2959, `emit_stay_table` 3516-3530.

Lens 1 is right that the extraction is safe and that **the identity gate
proves it rather than a reviewer asserting it** — which means the
refactor does not need a unit net, and I am not proposing one for it.
What the identity gate cannot prove is behaviour at table lengths the
corpus does not contain. The wrapping is `if (k % 16 == 0) sb_puts(c,
"\n       ");` over `d->n * d->ncls` cells (`emit_dfa.c:2616-2617`), and
the boundaries are `N = 0`, `N = 1`, `N = 15/16/17`, and `N ≡ 0 (mod
16)`.

**This is the K35 shape — a population nobody counted — and the honest
disposition is to count it first.** The measurement (D77): census the
distinct `d->n * d->ncls` values over the corpus and report which of
`{0, 1, 15, 16, 17}` and which residues mod 16 occur. If all five are
present, this item is **PROBED-AND-HELD** and the entry below moves to
§7. If `N = 0` or `N ≡ 0 (mod 16)` never occurs — and `N = 0` plausibly
never does, since a machine with no states does not reach the emitter —
then the extracted `emit_cell_table` is a function whose boundary
behaviour no artifact in the tree exercises, and one unit check over a
stub cell function covers all six sites at once.

I am filing it at POLISH and conditional rather than guessing the
population, because guessing it is what this lens is supposed to stop.

---

## 7. PROBED-AND-HELD

Seams examined and judged adequately covered, with the covering section
named, so a later wave does not re-argue them.

- **`src/core/cpset.c`'s interval algebra** — held by
  `tests/codegen/cpset_model_check.c` (`run_cpset_structure.sh:553`),
  which already does what this lens would recommend and does it better
  than a new check would: a 4,096-point flat-array oracle sharing no
  structure with the subject, membership **and** the sorted/disjoint/
  non-adjacent invariant, seven written-out edge cases including the
  `lo - 1` underflow at 0 and a 100-interval absorb, deterministic PRNG.
  **Held on coverage; see R0.2 for its sanitizer gap, which is a
  different finding about the same file.**
- **The caseless fold's byte relation** — held by
  `tests/backrefs/fold_agreement_check.c` and its `utf8` sibling
  (`run_backref_diff.sh:654`, `:682`): all 65,536 ordered pairs, one
  side read out of an artifact pcrec actually emitted, sabotage row S116
  moving exactly one byte. This is the model instance of a
  twin-implementation agreement check and R2 is written to its shape.
- **`pcrec_cwmin`/`pcrec_cwmax`** — held by `tests/mrl/cwmax_check.c`
  (`run_mrl_tests.sh:522`), per-block under the block's own encoding,
  with the span counted in the same unit. (Its sanitizer gap is R0.2's,
  not a coverage gap.)
- **`p_alt`'s branch count** — held by `tests/parse/branch_count_check.c`
  (`run_parse_tests.sh:55`), whose reference is a different algorithm
  cross-checked against two independent libpcre2 thresholds.
- **The registry's row invariants** — held by
  `tests/registry/registry_check.c`, 225 passing checks with a coverage
  guard and a manifest of irreplaceable needles
  (`run_registry_tests.sh:99-114`).
- **Both engines' answers, every rung, every axis** — held by the corpus
  (`tests/harness/run.sh`), the six single-process differential drivers
  (`possessify`, `rungselect`, `counterk`, `mrl`, `altcls`,
  `assertions` — `tt4_measurement.md` Stage A2 attributes them), and
  `make test-axes`'s answer-identity sweep. **A unit test of a rung's
  emitted shape would duplicate oracle coverage and is explicitly the
  thing this lens must not recommend.** Filed so a later wave does not
  read "more unit tests" as licence to test the engine below its
  answers.
- **The `volatile`-across-`setjmp` discipline** — held **mechanically**
  by `-Wclobbered` riding `-Wextra` in `WARN` (Makefile:16), promoted to
  `-Werror` by `make strict` (Makefile:1171-1175); lens 8's H2 verified all
  eleven crossing scalars. A compiler diagnostic is a better check than
  a test and no unit surface is proposed. (Lens 8's own caveat stands:
  `-Wclobbered` is vacuous at `-O0`, so a `make strict CFLAGS=-O0` is a
  silent pass — worth a one-line guard in the `strict` target, which is
  a lens 3/lens 8 item, not mine.)
- **The arena/heap ownership boundary** — held by lens 8's H3 (all 76
  `free()` sites classified) as a *review* result, and by ASan as a
  *running* one. A unit test cannot see a static ownership property, and
  R1's injector is what turns the failure-path half into a check.
- **`minimize.c`'s and `scanedge.c`'s hand-freed heap tables** — held by
  lens 8's H5/H6 on all three and all four exits respectively. These are
  the strongest candidates for R1's injector once it exists (each has a
  multi-table cleanup block that a partial-failure path must get exactly
  right), and until then they are review-held, not check-held. Stated
  this way rather than as "held", because the distinction is the whole
  point of R1.
- **Engine selection** — held by `tests/axes/run_axes.sh` plus the
  `RXTDUMP` stamps: the decision is caller-observable through a stamp,
  so it has an answer-level surface and does not need an internal one.
- **`src/core/sb.c`'s append/grow arithmetic** — held by ~1,063 call
  sites across the whole suite: every artifact the corpus compiles is a
  `StrBuf` end to end, so a length or NUL-termination bug is a
  corrupted artifact and `make test` is red everywhere at once. **Only
  its FAILURE path is uncovered**, which is R1. Filed explicitly because
  "sb.c has no unit test" reads like a gap and is not one.

---

## 8. ADMISSIBILITY NOTES

- **A1 (ruled record).** `decisions.md:4602` is the tree's only ruling
  touching a unit test; R0.5 cites it in full, distinguishes the two
  cases it separates, and makes the distinction a filing requirement for
  every item here. No other finding contradicts a D-row. R3 and R5 each
  cite a recorded authorial choice (`rxt_source.c:1364-1368`'s four
  deliberate copies; `atomic.c:28-36`'s no-`default:` rule) and are
  written to preserve rather than overturn them. R0.1's `-Werror`
  recommendation cites R5-Q1 and argues the test-compile/`make`
  distinction explicitly rather than ignoring it.
- **A2 (abstraction bar).** No duplication finding is filed here; R3,
  R4 and R5 are *specifications for primitives lens 1 and lens 2 have
  already named with signatures*, and R2 is a check that would be
  written whether or not X3's unification happens.
- **A3 (check coupling).** Every recommendation is ADDITIVE and stales
  nothing: verified by grep over all 261 rows in `tests/mech/sabotages/`
  — `src/core/sb.c` 0 rows, `src/core/arena.c` 0, `src/core/cpset.c` 0,
  `src/opt/minimize.c` 0. The refactors these checks are nets FOR do
  carry re-aims (X3 → S58/S59/S-U4; X1 → S91/S97/S104/S158/S159/S174;
  X5 → S201; the fragment layer → 24 anchors per lens 2 §4.1), and
  those travel in their own waves. **R1 and R2 each propose a NEW
  sabotage row** — the first rows ever to plant in `arena.c`/`sb.c` and
  the first to defend the saturating arithmetic's agreement — and both
  must be numbered against the highest existing S-id **on main** at
  their own landing (BOILERPLATE's rule), not against anything in this
  report.
- **A4 (severity/effort/blast).** Stated per recommendation. Ranked in
  §9.
- **A5 (evidence).** `function_census.tsv` rows are quoted inline with
  their line spans; `clone_candidates.tsv` groups are cited by number
  and `group_frac`. The ten-file tier population, the four flag
  policies, the `san_scripts.txt` membership and the sabotage-file
  distribution are direct greps at `7d444f9e`, each with its command's
  result stated rather than summarized.

---

## 9. RANKED FOR THE SYNTHESIS

1. **R0.2** — two lines in `san_scripts.txt`. The only CORRECTNESS-RISK
   item here that is already true rather than prospective: the tree's
   best unit check has never run under a sanitizer.
2. **R2** — the saturating-arithmetic agreement. One new file,
   microseconds, checks a correctness requirement the tree states twice
   in prose and enforces nowhere, and is the precondition that makes X3
   safe.
3. **R0.1 / R0.3 / R0.4** — `unit_cc.sh`, `tests/core/`, the budget
   rule. Mechanical, and every later item lands in it.
4. **R1** — allocation-failure injection, staged behind lens 8's
   F6(a)/(b)/(c). Reclassified from DESIGN-EVENT to LOCAL on the
   `-include` + `BUILD_DIR` spelling; the only instrument that finds an
   F1 directly.
5. **R4.1** — `txt_f`'s no-truncation ladder. Rides wave 1; it is what
   makes lens 2's step-3 acceptance number mechanically true.
6. **R4.2 / R4.3** — the field/row and join properties. Ride wave 1
   step 1, after lens 2's own population measurement.
7. **R3** — the arena vector's four properties. Rides whichever wave
   builds the primitive; **not written against today's thirteen copies.**
8. **R5** — the AST traversal's two properties. Written against X2's
   merged `pcrec_ast_visit`, inherited by X1's `pcrec_ast_walk`.
9. **R6** — the table emitter's wrapping boundaries. CONDITIONAL on a
   population census not taken here.

---

## 10. ADDENDUM 2 — WHERE THE SWEEP STOPPED

**Reviewed exhaustively.** The *check* population, found by grep rather
than by census rank: every `.c` file under `tests/` (79 files), every one
that `#include`s `core/internal.h` (10), every build site for those ten,
`tests/lib/san_scripts.txt` in full (35 entries), and the `SAB_FILE`
distribution over all 261 sabotage rows. That population is complete, not
sampled, and it is the population this lens is about.

**Reviewed against the subject side.** All of `src/core/` (`arena.c` 44
lines, `sb.c` 81, `cpset.c` 309, `fold.c` 144, `tune.c` 180 — read;
`compile.c` 1,892 read only at the `Ctx`/`Job`/`setjmp` seam via lens
8's citations), the three saturating-arithmetic families in full, the six
DFA table emitters, the thirteen growable-array rows, and the walk
family via lens 1's tabulation rather than by re-reading eleven
predicates.

**Per ADDENDUM 2, the named remainder:**

1. **`src/gen/emit_vm.c` below the stamp and arithmetic layers.** 11,575
   lines, the tree's longest function, 85 of 261 sabotage rows. I read
   `vm_fadd`/`vm_fmul` and nothing else. **Lens 1 named this as needing
   its own second pass and I am naming the same need from this lens's
   side**: the VM's rung/slot/frame emission is the largest body of code
   in the tree with no internal-property check of any kind, and I cannot
   say from here whether that is a gap or correct (the byte-identity
   gates may cover it entirely). Deciding that is a second pass, not a
   skim.
2. **`src/ir/nfa.c` and `src/ir/dfa.c`.** Reached only through
   `patch_push` and `cont_push` for R3's census. `compile_ast` (121 code
   lines) and `intern` (84) were not read, and `intern` in particular —
   `dfa.c:809`/`:871`, the state-identity function the whole DFA rests
   on — is the one seam I would look at first in a second pass. It has
   the shape R2 and R3 are about: a helper whose *correctness* is a
   property (equal states intern equal, unequal states intern unequal)
   that answers only reveal statistically.
3. **`src/parse/rxt_source.c`'s text-handling family.** Lens 1 named
   groups 13/14 (`value_trimmed`, `rtrim_ws`, `prose_value`,
   `read_wrapped_value`, `ident_ok`, `defname_ok`, `oracle_ref_ok`) as a
   real text family it did not judge. Several of those are total
   functions over strings — the easiest things in the tree to unit-check
   — and K57 (a block scalar's dedent strip silently deleting content,
   fixed 2026-09-15) is a shipped bug of exactly that shape. I did not
   review them; a lens 5 second pass should start there rather than at
   the emitters.
4. **`tests/lib/` and `tests/harness/`.** Out of scope by charter
   (secondary tier, dispositioned to next round) — noted because
   `unit_cc.sh` would live there and its own review belongs to that
   round.
5. **The census tail.** I did not work the 860-row census top-down; this
   lens's population is helpers, which are at the *short* end of the
   length ranking (`mrl_sat_add` is 5 code lines, `cpset_grow` 10,
   `sb_grow` 15). ADDENDUM 2's length ordering is the wrong ranking for
   this lens and I used the clone groups and the grep censuses instead,
   which is a deliberate departure and is stated here rather than
   silently taken.
