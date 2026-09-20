# axtriage — triage of the stage-5 merge battery's `axes` stage (rc=2)

2026-09-09, lane axtriage. Log-reading + code diagnosis, then a targeted
fix in worktree `worktrees/axtriage` / branch `lane/axtriage`. Never
merged to main.

## Scope note

The brief asked me to triage `build/battery_20260909_s5/axes.log` (rc=2,
15:13->20:58) and weigh four prime suspects: (1) `axes_registry_check`'s
pin, (2) an answer-identity diff under a deny/force flag, (3) tt4m3's
run.sh refactor changing harness behaviour under `test-axes`'s own env
knobs, (4) the form census/floors moved by stage 5's new corpus.

**None of the four is what actually failed.** `build/battery_20260909_s5/
axes.log` is entirely `tests/axes/run_axes.sh`'s own output (`make
test-axes`, a DIFFERENT check from `axes_registry_check`, which lives
under `tests/registry/` and never appears in this log at all — suspect
(1) does not apply to this stage). The log's own registry-derivation
line at the top (`axes: registry derived — 22 bit-flag axes...`) reads
clean and matches tuning.md's own count; nothing about the bit-flag
registry moved.

## The one failure

Every one of the 22 bit-flag axes plus `--engine=dfa` plus all four
`--vm-entry-shape` rungs (`AXES_FULL=1`, the battery's own tier) reads
`OK` with `agree=24194` (or the axis's own documented refused
population) and `mismatches=0`. The ONLY `AXIS FAIL` in the whole
20,696-second run is `--engine=vm`:

```
AXIS FAIL: --engine=vm (§2.11): UNDOCUMENTED refusal at
tests/utf8/axis12_scripts.rxt:295: "pcrec: pattern too large: 689367
bytes of emitted code (limit 500000), ... " (does not match any of this
axis's documented limits — this axis has NO documented refusal
population at all)
```
(and identically at :296, :297 — the same block's three cells).

`keys_base=24194 keys_axis=24194 agree=24181 budget=10 refused=3
mismatches=3` — **zero answer disagreements, zero lost/gained cases**.
The whole failure is three REFUSED cases the comparator could not
classify because `run_axes.sh`'s `REFUSAL_PATTERN` table had no entry
for `--engine=vm` at all.

## Root cause

`tests/utf8/axis12_scripts.rxt:292-297` (stage 5's script-properties
corpus, merged 0b21c32f) carries:

```
pattern \P{Unknown}
encoding utf8
features unicode-props
n "\xee\x80\x80"
m "\xce\xb1" 0 2
n "\xcd\xb8"
```

`\P{Unknown}` (the negated derived-complement script set — K53's own
finding that `Unknown` is the one script property shaped like `\p{C}`,
729 script-spanning intervals) compiles fine under DEFAULT axes: `auto`
engine selection never needs a VM artifact for it, so the file's own
comment notes only the BARE `\p{Unknown}` form (not negated) exceeds the
size cap at default axes and lives in `tests/known_fail/
k53_uprops_oversize.rxt`. Nobody anticipated the NEGATED form under a
FORCED `--engine=vm` axis, because forcing VM had never been exercised
by anything this large before.

Forcing `--engine=vm` makes the VM emitter the ONLY option (no DFA
fallback), and its emission for this class is 689,367 bytes against
`PCREC_MAX_VM_EMIT_CODE_BYTES = 500000` (`src/core/limits.def:158`) — a
real, working, pre-existing cap, verified live:

```
$ build/pcrec --engine=vm --features unicode-props -e utf8 -p rx \
    -o /tmp/x.c -- '\P{Unknown}'
pcrec: pattern too large: 689374 bytes of emitted code (limit 500000), ...
```

(689374 here vs. the battery's 689367 — negligible drift between the
battery's commit and HEAD of `lane/axtriage`, irrelevant to the
substring match either way.)

**This is legitimate, not a defect.** `run_axes.sh`'s own header comment
for the coarse engine axis already said so before stage 5 ever landed:
tuning.md §2.11 documents `--engine=vm` as "in principle" capable of
refusing, "though no corpus member is expected to exercise it" — stage 5
is simply the first corpus addition that does. It is also NOT K53 (the
DFA's OPTIONAL anchored machine breaking ITS OWN no-refusal promise) —
this is `--engine=vm` hitting its own MANDATORY size ceiling exactly as
designed.

## Verdict: check-registry gap, not an engine regression

Classified against the brief's own taxonomy: **neither a stale pin, nor
a real answer-identity regression, nor a harness-behavior change from
tt4m3, nor a form-census/floor movement.** It is the fourth case K45
already set precedent for: a `REFUSAL_PATTERN` table entry the design
always expected to eventually need, now needed for the first time.

## Fix

One entry added to `tests/axes/run_axes.sh`'s `REFUSAL_PATTERN` table:

```
["--engine=vm"]="bytes of emitted code (limit"
```

— the identical substring `-fno-size-term`'s existing entry uses (same
cap family, K45's landed precedent shape: document the mechanism, no
bare re-pin). No `REFUSAL_FLOOR` raised: K35 requires a MEASURED
population and the only measurement here is this one file's 3 cells, not
a corpus-wide sweep (same discipline K45's own two file-scoped entries
followed).

Documented in two places, mirroring K45's own record:
- `docs/dev/known_issues.md` — new entry **K55** (filed and FIXED in the
  same lane, same shape as K45's own entry).
- `tests/axes/CLAUDE.md` — new "K55" section beside the existing "K45"
  one, same format.

## Validation

The box was under a concurrent `mech` hold for this lane's entire working
period (stage-5 battery, `build/battery_20260909_s5/`), so a full-corpus
`make test-axes` re-run was out of scope per the brief ("plan targeted
axes, not the full sweep"). Targeted validation performed:

1. Built the worktree clean: `make -j4 CC=gcc-16` — no warnings, no
   errors.
2. Reproduced the exact diagnostic text live against the built `pcrec`
   (above) — confirms the substring match is correct.
3. `AXES="--engine=vm" SKIP_ORACLE=1 PROCS=4 bash tests/axes/run_axes.sh
   tests/utf8/axis12_scripts.rxt` (single file, single axis, ~24s wall):

   ```
   --engine=vm (§2.11)|OK|keys_base=53 keys_axis=53 agree=50 budget=0
     refused=3 lost=0 gained=0 mismatches=0 refused_doc=3 refused_undoc=0
   ```

   Before the fix this read `AXIS FAIL` with `refused_undoc=3`; after,
   `OK` with `refused_doc=3 refused_undoc=0` — exactly the three cells
   named above, reclassified correctly.

   (The same run also shows `--engine=dfa` as `FAIL` on this restricted
   population — `refused_documented=0 is BELOW its K35 floor (8000)`.
   That is NOT a regression from this change: `--engine=dfa`'s floor is a
   full-corpus number (8000), and a single 53-case file cannot meet it by
   construction. It is an artifact of running `AXES=`+single-file rather
   than the full corpus, exactly as `tests/axes/CLAUDE.md`'s own K-SWEEP
   section describes for floor checks. A full-corpus run does not hit
   this.)

**OWED to the manager**: a full-corpus `AXES_FULL=1 make test-axes`
confirmation once the box is free (the stage-5 battery's own re-run, or
a dedicated `test-axes` pass) — expected result: `--engine=vm` reads
`refused_doc=3 refused_undoc=0`, every other axis unchanged from the
battery's own log (`build/battery_20260909_s5/axes.log` lines 250-277,
all already `OK`).

## Validation status

**BUILT AND TARGETED-VALIDATED, full-corpus confirmation OWED** (box
held by the concurrent stage-5 `mech` run for this lane's whole working
period — see above for the exact command and expected result).

## Commits

On branch `lane/axtriage`:
- `tests/axes/run_axes.sh`: the one `REFUSAL_PATTERN["--engine=vm"]` entry.
- `docs/dev/known_issues.md`: K55 filed and fixed.
- `tests/axes/CLAUDE.md`: K55 section.
- This report.

---

# axtriage (2026-09-19/20 relaunch) — TRIAGE of a DIFFERENT red in the
# Linux battery's `axes` stage

This lane name was reused by the manager for an unrelated, later triage
(the section above is the 2026-09-09 K55 lane's own record, kept
verbatim — historical, per `docs/dev/lanes/CLAUDE.md`'s "historical once
merged" rule; do not conflate the two). This section is the 2026-09-19/20
work, on the SAME worktree/branch name (`worktrees/axtriage`,
`lane/axtriage`) but starting fresh from a much later `main`
(25b1984f), for a different failing axis on a different corpus file.

2026-09-19/20, lane `axtriage`. Triaging one red at pcrec main 25b1984f:

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
own report above: "Full-corpus confirmation is the manager's, at the next
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
comment block, this report update. No spec edit (none needed). `make
strict` green. Single-file positive/negative control confirms the fix;
full-corpus floor confirmation and `test-codegen` are owed per the
concurrency note above.
