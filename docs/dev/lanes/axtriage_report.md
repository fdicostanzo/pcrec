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
this is `--engine=vm` hitting its own MANDATORY, always-documented size
ceiling exactly as designed.

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
