# axtriage — TRIAGE of one red in the Linux battery's `axes` stage

2026-09-19/20, lane `axtriage`, worktree `worktrees/axtriage`, branch
`lane/axtriage`. Triaging one red at pcrec main 25b1984f:

```
AXIS FAIL: --engine=dfa (§2.11): UNDOCUMENTED refusal at
tests/base/opt41_rung_nullable_decline.rxt:41: "pcrec: pattern too complex
for the DFA engine (>32000 states; try --engine=vm) (pattern offset 0)"
(does not match any of this axis's documented limits)
— identical for :42 :43 :44 :45 :46 — 6 mismatch(es), 0 lost-other, 0 gained
```

## Diagnosis

`tests/base/opt41_rung_nullable_decline.rxt` is NEW at this pin (lane
`adm71`, commit e021b982): `(?:ab){0,16000}` is built to overflow
`PCREC_MAX_DFA_STATES_TABLE` (32000 states, `src/core/limits.def`) so that
under `--engine=auto`, `compile_driver` offers the [SEL-1] collapse rung and
the pattern declines it (`[OPT-4.1]`'s reachability witness — see the file's
own header). Under `auto` this is a SELECTION OUTCOME and the pattern
answers correctly via the VM fallback. Forcing `--engine=dfa` has no
fallback and refuses do-or-die, at `src/ir/dfa.c:954`:

```c
ctx_fail(cx, 0, "pattern too complex for the DFA engine (>%d states; "
         "try --engine=vm)", d->maxstates);
```

**This is NOT a spec gap (D80).** `docs/spec/tuning.md` §2.11 already
documents this exact diagnostic verbatim, inside its own `[SEL-1]`
subsection (§2.11 spans lines 556-670; `[SEL-1]` sits at line 580, so it is
part of §2.11, not a separate section): "`--engine=dfa` and `-fprefilter`
are UNCHANGED by this — both still refuse with today's diagnostic
(`"pattern too complex for the DFA engine (>N states; try --engine=vm)"`)".
No `docs/spec/` edit was needed or made.

**The bug was entirely in `tests/axes/run_axes.sh`'s derived-registry
check** (`docs/dev/learnings.md` §3: a check must be derived from the spec,
never a hard-coded exception for one corpus file — and it already was
derived, just incomplete). Its `--engine=dfa` `REFUSAL_PATTERN` entry
carries a 2026-09-03 (K45) comment that had *already anticipated this exact
limit and declined to add it*:

> A third documented DFA limit exists in src/ir/dfa.c ("pattern too complex
> for the DFA engine", the state-count/subset-construction ceiling) with
> ZERO corpus population today — not added as a pattern, since a
> zero-population entry cannot be verified live and this axis's own floor
> is left unset for the same reason (K35: a floor asserts a MEASURED
> population, never a guessed one).

That same comment block also records a "THIRD shape now populated"
addendum from the same day, where `size_term.rxt`'s tower reached this
limit's *NFA-build sibling cap* (`src/ir/nfa.c`'s "pattern too large (NFA
exceeds ... states)") through a different door — not the state-cap site
itself. `opt41_rung_nullable_decline.rxt` is the first corpus member to
reach the DFA state-cap `ctx_fail` site directly, giving the
zero-population entry a real, measured population for the first time.

**Fix**: added `"pattern too complex for the DFA engine"` to
`--engine=dfa`'s `REFUSAL_PATTERN` entry
(`tests/axes/run_axes.sh:467`, now with a fourth `${REFUSAL_DELIM}`
clause and a dated comment recording this). The exact same substring
already sits in `-fprefilter`'s own `REFUSAL_PATTERN` entry (added at
[SEL-1] itself, 2026-08-28) — `-fprefilter` needed no change.

## Validation

**Reproduction, live:**
```
$ build/pcrec -p rx --engine=dfa -o - -- '(?:ab){0,16000}'
pcrec: pattern too complex for the DFA engine (>32000 states; try --engine=vm) (pattern offset 0)
```

**Positive control (before the fix, worktree HEAD^, this file's engine=dfa
axis only):**
```
$ SKIP_ORACLE=1 AXES="--engine=dfa" bash tests/axes/run_axes.sh tests/base/opt41_rung_nullable_decline.rxt
...
AXIS FAIL: --engine=dfa (§2.11): UNDOCUMENTED refusal at ...:41/42/43/44/45/46 ...
  --engine=dfa (§2.11)|FAIL|... refused_doc=0 refused_undoc=6|1s
```

**After the fix, same command:**
```
  --engine=dfa (§2.11)|FAIL|keys_base=6 keys_axis=6 agree=0 budget=0 refused=6
    lost=0 gained=0 mismatches=0 refused_doc=6 refused_undoc=0|1s
AXIS FAIL: --engine=dfa (§2.11): refused_documented=6 is BELOW its K35
  floor (8000) — the documented refusal population shrank
```

The UNDOCUMENTED-refusal defect this lane was triaging is gone
(`refused_undoc`: 6 → 0, `refused_doc`: 0 → 6). The axis still prints
`FAIL` on this single-file run, but for a DIFFERENT, expected reason:
`--engine=dfa`'s `REFUSAL_FLOOR` (8000) is a CORPUS-WIDE measured
invariant (the pre-existing population is ~3,874 + 5,594 + a handful of
K45 cells), and this one 6-case file cannot clear it alone — the identical
floor-vs-scope artifact the K45 and K55 entries immediately above this
one in the same file document and defer to a full-corpus run for (K55's
own report: "Full-corpus confirmation is the manager's, at the next
battery"). This is not a regression: the fix can only ever RAISE
`--engine=dfa`'s measured `refused_documented` population (these 6 cases
move from "undocumented failure" to "documented, counted"), never lower
it, so the floor cannot be newly broken by this change on the full corpus.

**Item (d) — checked every other axis against the same file** (no `AXES=`
filter, single file, cheap):

```
$ SKIP_ORACLE=1 bash tests/axes/run_axes.sh tests/base/opt41_rung_nullable_decline.rxt
```

Every axis reads `refused_undoc=0`, 0 mismatches, 0 lost, 0 gained on this
file. Three lines print `FAIL` in the summary: `-fno-counter`,
`-fprefilter`, `--engine=dfa` — all three, and only these three, are the
identical floor-vs-scope artifact (their own `REFUSAL_FLOOR`s are 180,
12000, 8000 respectively; this file supplies 0, 6, 6 cases against them).
`-fprefilter`'s refusal on this file already matched its existing
`"pattern too complex for the DFA engine"` substring before this change —
it needed no fix. No genuine mismatch/lost/gained anywhere. `--engine=vm`
is fine, matching adm71's own report.

**`make strict`** (CC=gcc-16): `strict: whole tree compiles clean with
-Werror -Wshadow` — unaffected by this change (a bash-script-only diff;
no `src/`/`cli/` file touched).

**No `docs/spec/` change** — see Diagnosis above; the diagnostic was
already documented, so `tests/registry/run_registry_tests.sh` was not run
(nothing for it to cross-check).

## Owed to the next battery (not run here)

`worktrees/w5` was running a full `make test` on this box for the entire
duration of this lane's work (`ps` confirmed it live, `timeout 5400 make
test`). Per box-concurrency rule 9 (memory `pcrec-box-concurrency`: "lanes
export PROCS=4 for any harness suite, and run none while a battery
runs") and rule 11 (a HOLD-shaped situation — a harness section forks
`PROCS=nproc` workers and IS a heavy run), this lane did NOT run:

- **`make test-axes`** (or even a full-corpus single-axis
  `AXES="--engine=dfa"` sweep with no file argument) — this is what would
  clear the K35 floor line above and give a clean `OK` on `--engine=dfa`
  for the whole corpus. Expected: `refused_documented` rises by exactly 6
  over the pre-fix reference count, `refused_undoc=0`, floor (8000) still
  cleared.
- **`make test-codegen`** — not actually implicated by this change (the
  diff touches only `tests/axes/run_axes.sh`, no emitted-code/scaffolding
  change, so D76/D94's abi-bump trigger does not apply here), but listed
  in the brief's validation bar; deferred for the same concurrency reason.

Both are single-command, low-judgment re-runs once the box is free — no
design question is open.

## Deliverable

One commit on `lane/axtriage` (`1e4e2dd0`): the `REFUSAL_PATTERN` fix, its
comment block, this report. No spec edit (none needed). `make strict`
green. Single-file positive/negative control confirms the fix; full-corpus
floor confirmation and `test-codegen` are owed per the concurrency note
above.
