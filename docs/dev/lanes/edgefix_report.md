# edgefix — triage of the O-42 scan_edge_ladder harness faults

Lane `edgefix` (sonnet), triage-only against `studies/scan_edge_ladder/`.
Branch `lane/edgefix` from main `dbc4865a`. Nothing under `src/` changed.

## Summary (one line each)

1. **LADDER "COMPILE FAILED" on every rung, rc=0 anyway**: `run_ladder.sh`'s
   `ARM[before]`/`ARM[after]` paths were built from a RELATIVE `$OUT`
   before the script's own `cd` into `$OUT/work`; `make ladder` always
   passes the Makefile's non-empty `OUT=out` default, so the two reference
   binaries resolved one directory too deep and were never found.
2. **FLOOR "forward edges = 0" on every cell, rc=0 anyway**: the edge-count
   census reads the `[OPT-5] SCAN EDGE` **comment** marker, and D112
   (2026-09-19, abi 26 -> 27) made emitted comments non-default; the
   floor's census reads `$PCREC`'s own artifact (no old-reference
   stand-in), so it reads 0 unconditionally once comments are off.
3. **The harness reported success (`rc=0`) while measuring nothing** in
   both cases — a defect in its own right (`docs/dev/learnings.md` sec 3).

What changed: `$OUT` absolute-ized in both run scripts; `-fcomments`
added to the one `$PCREC` build the floor's census reads; every "measures
nothing" branch now sets a non-zero exit code; `run_floor.sh` gained the
median/IQR summary block. README and `studies/CLAUDE.md` updated.

## Fault 1 — the ladder's relative-`$OUT` bug

**Evidence, quoted from `out/ladder_run1.log`** (ubuntubudu, eaab0d4a,
fetched read-only over the tailnet):

```
c_before already built
c_after already built
rung 1  \d{2}y                     forward edges = 1  OK
...
OUT=out PCREC=/home/duxevents/pcrec/build/pcrec ./run_ladder.sh
rung 1 arm before: COMPILE FAILED
rung 1 arm after: COMPILE FAILED
rung 1  pattern \d{2}y                       forward edges = 1  (want 1)
```

Note the shape: `make rungs` (the block before the `OUT=... ./run_ladder.sh`
line) built `a_before_1.c`/`a_after_1.c` successfully via the Makefile's own
recipe and reported the correct edge counts. `run_ladder.sh` then re-derives
the SAME two artifacts itself (its own header comment explains why: `make
ladder` depends on `rungs`, then re-generates independently) — and THAT
second generation is where it fails.

**Root cause.** `run_ladder.sh` line 22 reads `OUT=${OUT:-$HERE/out}`. This
default only fires when `$OUT` is UNSET. `make ladder`'s recipe is
`OUT=$(OUT) PCREC=$(PCREC) ./run_ladder.sh`, and the Makefile's own
`OUT ?= out` (line 17) means `$(OUT)` is always the non-empty string
`out` — so the script's env receives `OUT=out`, a value, and the
`${OUT:-...}` fallback never triggers. `$OUT` stays the RELATIVE string
`out`.

The script then builds the `ARM` associative array (lines 40-44) BEFORE
doing anything else with `$OUT`:

```
declare -A ARM=(
  [before]="$OUT/c_before/build/pcrec"
  [after]="$OUT/c_after/build/pcrec"
  [step11]="$PCREC"
)
```

With `$OUT=out`, `ARM[before]="out/c_before/build/pcrec"` — a path
relative to whatever the CURRENT working directory is at the moment the
array is built (the study directory, since `make` invokes the recipe
there). That's fine *until* line 106: `mkdir -p "$OUT/work"; cd
"$OUT/work"`. After this `cd`, the process's cwd is
`studies/scan_edge_ladder/out/work`. `ARM[before]`'s stored string is
still the literal text `out/c_before/build/pcrec` — bash does not
re-resolve a string when the cwd changes — so referencing
`"${ARM[before]}"` at line 111 now resolves to
`studies/scan_edge_ladder/out/work/out/c_before/build/pcrec`, which does
not exist. The shell reports "No such file or directory", the command's
exit status is non-zero, and the script's own guard
(`|| { echo "rung $k arm $arm: COMPILE FAILED"; continue; }`) fires.

This is **the mirror image of a bug the script already documents and
fixed** — its own header comment (lines 29-37, unchanged by this lane)
explains that `$PCREC` needed exactly this same absolute-ization for
exactly this same reason, found 2026-09-04. `ARM[step11]="$PCREC"` was
therefore already safe; `ARM[before]`/`ARM[after]`, built from `$OUT`
rather than from an already-hardened variable, were not.

Confirmed this is the WHOLE explanation, not a symptom of something else
(e.g. an API/ABI drift in the "pcrec_" export-prefix wave, or a gcc-15
incompatibility in the old reference trees): the rung census at the top
of `ladder_run1.log` (`make rungs`'s own successful build, in the
Makefile's cwd, unaffected by the bug) shows `before`/`after` compiling
`\d{2}y` etc. cleanly with the identical CLI invocation `run_ladder.sh`
later fails on. `9d8401a`/`b048fa61` (the two archived reference commits)
both already support `--features`, `-p`/`-o`/`-e`, and `--features all`
(checked directly against those commits' own `cli/main.c`/
`src/parse/enabled.c`) — there is no CLI incompatibility to find.

**Fix.** Absolute-ize `$OUT` immediately after it is read, the same way
`$PCREC` already is, in both `run_ladder.sh` and (symmetrically, before a
future edit exploits it there too) `run_floor.sh`:

```sh
case "$OUT" in
  /*) : ;;
  *)  OUT="$HERE/$OUT" ;;
esac
```

`run_floor.sh` does not reference `$OUT` again after its own `cd`, so it
was not exhibiting this bug today — but it receives the identical
`OUT=out` from `make floor`, so the fragility was latent and is hardened
for the same reason.

## Fault 2 — the edge-count census reads a comment, and comments are off by default

**Evidence, quoted from `out/floor_run1.log`**:

```
m=2  exact    [0-9]{2}x      forward edges = 0  *** TAKES NO EDGE, cell measures nothing ***
m=2  nullable [a-z]{0,2}     forward edges = 0  *** TAKES NO EDGE, cell measures nothing ***
m=3  exact    [0-9]{3}x      forward edges = 0  *** TAKES NO EDGE, cell measures nothing ***
...
```

(all eight `m x family` cells, both `floorcells`'s pre-check and
`run_floor.sh`'s own re-check, both floor runs — the pattern spellings
here are the SAME ones the study's own README documents as verified to
take exactly one edge each, so this is not a population/spelling
regression.)

**Root cause.** The census is one line, present in three places
(`Makefile`'s `floorcells` target, `run_ladder.sh`'s rung re-check, and
`run_floor.sh`'s cell re-check):

```sh
awk '/\[OPT-5\] SCAN EDGE/{p=1;next} p && /if \(forward_state ==/{n++;p=0} END{print n+0}' FILE
```

It counts occurrences of the literal text `[OPT-5] SCAN EDGE`, which
`src/gen/emit_dfa.c:5791`/`:5796` emits as a **comment**
(`pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL)` wraps it — confirmed by
reading the emitter directly). D112 (`docs/dev/decisions.md`, 2026-09-19,
abi 26 -> 27, lane `emitverb`) ruled emitted comments OFF by default; the
opt-in force flag is `-fcomments` (confirmed against
`src/core/axes.def:157-158`: `PCREC_AXIS(PCREC_NO_COMMENTS,
"-fno-comments", PCREC_FORCE_COMMENTS, "-fcomments",
PCREC_AXIS_DEFAULT_OFF)`). Any artifact `$PCREC` emits at default flags
since abi 27 therefore carries no `[OPT-5] SCAN EDGE` text at all, and the
awk census reads 0 regardless of the machine's real edge count.

I looked for a non-comment stamp that would survive comments-off and
carry the same fact (per the brief's instruction to prefer a stamp over a
flag if one exists) — `f->nscan` (the true, structurally-computed edge
count, `src/gen/emit_dfa.c:5922-5923`) is never itself emitted as a
`#define` or any other non-comment text; the nearest candidate,
`token_stop`'s `is_stop(s) { return (unsigned)s >= %uu; }` accessor
(`emit_dfa.c:3976-4011`), emits a real (non-comment) numeric floor, but
that floor is `f->repr->cell_of(f->d->n - f->nscan, f->d)` — a
representation-dependent CELL value (premultiplied tables transform row
numbers non-linearly), not the count itself, and recovering `nscan` from
it would require also knowing `f->d->n` (total states) and re-deriving
the representation's own cell arithmetic — i.e., reimplementing a slice
of `scanedge.c`/`emit_dfa.c` inside a shell census. That is a special-case
duplicate mechanism, not a general one, and is exactly what this house's
own convention (`pcrec-general-mechanisms-not-special-cases`) warns
against building for a measurement instrument. **No new stamp exists for
this and none is proposed here** — per the brief, nothing was added under
`src/`.

**Fix (measurement-side only).** Ask the existing mechanism for the fact
it already carries, on the one build where it matters: add `-fcomments`
to `floorcells`'s and `run_floor.sh`'s `$PCREC ... -o e_${fam}_$m.c ...`
invocation (the artifact the census reads). This is the ONLY place that
needs it:

* `rungs`'s and `run_ladder.sh`'s own rung census read `a_after_$k.c`,
  built by the archived `after` reference compiler (`b048fa61`), which
  predates D112 entirely and always emits comments unconditionally — it
  has no `-fcomments` flag to accept, and passing one would itself be a
  hard CLI error on that old binary. The ladder's design already relies
  on `step11` sharing `scanedge.c`'s edge-taking decision with `after` by
  precondition (the README's own "1.1 this branch ... must sit on top of
  AFTER"), so `after`'s topology is the correct stand-in and needed no
  change.
* `-fcomments` is proven byte/behaviour-neutral for the artifact under
  test: D108 (the emission-kit's render-time comment gate) and
  `docs/dev/lanes/emitverb_report.md` §3a's own `.o`-identity proof (plus
  its fix for the one place a raw-byte-INCLUDING-comments size comparison
  could have selected a different entry-shape rung) — both already on
  this branch's ancestry (`dbc4865a` postdates lane `emitverb`'s merge).
  So turning comments back on for this one build changes only what the
  census can SEE, not what is measured.

## Fault 3 (harness discipline) — success reported with nothing measured

Both `run_ladder.sh` and `run_floor.sh` printed their "measures nothing"
lines and then exited 0 (`make ladder`/`make floor` likewise). Fixed by
accumulating an `RC` variable set at every failure point (build failure,
wrong edge count, zero valid rounds for a ladder rung, "takes no edge" or
"never entered" for a floor cell) and `exit`ing with it; `Makefile`'s
`rungs`/`floorcells` targets get the equivalent `bad=1 ... exit 1` guard.

## The m=2 bimodal signature — recorded, not analysed (per the brief)

Both fetched floor logs show it raw. `floor_run1.log`, m=2 exact, rounds
12-15:

```
   12  2  exact     4.1810   4.2021     0.9950
   13  2  exact     4.1698   2.2986     1.8141
   14  2  exact     4.1843   2.3010     1.8185
   15  2  exact     4.1689   4.1729     0.9990
```

`floor_run2.log`, m=2 exact, rounds 1-8 (mixed ~0.90-1.00 and ~1.7-2.6):

```
    1  2  exact     4.9303   1.8988     2.5965
    2  2  exact     4.7723   1.8937     2.5200
    3  2  exact     4.2062   2.2995     1.8292
    4  2  exact     4.1876   2.3083     1.8142
    5  2  exact     3.2318   1.8941     1.7063
    6  2  exact     4.1669   4.1552     1.0028
    7  2  exact     4.1794   2.3975     1.7432
    8  2  exact     3.4455   1.8929     1.8203
```

m=3/4/8 (both families) hold ~0.92-1.02 throughout both logs. This is the
SAME signature `docs/dev/lanes/edge2_report.md` §9.3 already recorded on
2026-09-04 (median 1.78, IQR 0.87, "bimodal ... this reads like a shared
measurement instability ... plausibly because `[0-9]{2}x}`'s 256 KB sweep
is the shortest-running cell of the eight"), reproducing at a different
pin and toolchain. Per the brief, this is stated as evidence for the
manager/Frank to interpret, not diagnosed further here.

## Where the 2026-09-04 medians/IQR came from

`edge2_report.md` §9.2/§9.3 states it directly: "full script run
interactively; not saved as a file per the brief's no-write scope —
reproducible from the same regex against the three logs" — an interactive
`python3 -c "..."` one-liner run BY HAND against the raw per-round stdout
the harness already printed, never committed. That is why re-running
`run_floor.sh` never reproduced a summary block: the harness itself never
had one. `run_floor.sh` now computes and prints one (median + a
linear-interpolated IQR, per `m x family`, over accepted rounds only) as
part of its own output — see the README's new "The floor's median/IQR
summary" section.

## Mac verification (darwin, gcc-16, after the gate)

The box was under a `make test` gate (`build/gate_4c2b06d2`) for this
lane's whole working period; per BOILERPLATE, no build or harness compile
stage ran until it printed `== GATE END`.

<!-- VERIFICATION-TRANSCRIPT-PLACEHOLDER: filled after the gate clears -->

The timing stages (`run_ladder.sh`'s/`run_floor.sh`'s round loops) use
Linux-only `taskset -c`; per the brief, these are NOT ported to darwin.
Verification here is the COMPILE + COUNT paths only: `make refs`, `make
rungs`, `make floorcells`, and the `e_${fam}_$m.c` edge-count reads, with
the actual counts printed.

## Rulings received

None mid-flight; no rulings file was polled because none was needed.

## Re-run command block (same shape as I-81's (a), pin `<PIN>`)

```
git -C /home/duxevents/pcrec fetch origin && git -C /home/duxevents/pcrec checkout main && git -C /home/duxevents/pcrec pull --ff-only origin main && git -C /home/duxevents/pcrec rev-parse HEAD
# expect: <PIN> (must include this lane's merge; if not, STOP and report the hash)
uptime    # load1 must read < 0.5; if not, wait, do not launch
cd /home/duxevents/pcrec && make -j8 2>&1 | tail -3
cd /home/duxevents/pcrec/studies/scan_edge_ladder
timeout 1800 make refs   2>&1 | tail -5
timeout 900  make rungs  2>&1 | tail -20
timeout 3600 make ladder PCREC=/home/duxevents/pcrec/build/pcrec 2>&1 | tee out/ladder_run1.log | tail -40
timeout 900  make floorcells 2>&1 | tail -20
timeout 3600 make floor  PCREC=/home/duxevents/pcrec/build/pcrec 2>&1 | tee out/floor_run1.log | tail -40
uptime
timeout 3600 make floor  PCREC=/home/duxevents/pcrec/build/pcrec 2>&1 | tee out/floor_run2.log | tail -40
uptime
```

Expected differences from O-42's run: every `rung`/`m x family` line
reads a real, non-zero edge count and no "COMPILE FAILED"/"TAKES NO
EDGE"/"NEVER ENTERED" line should appear on the population the README
already verified (any that does appear is now a real finding, since the
harness fails the run rather than hiding it). Each `make` target now
returns non-zero on a bad population — a non-zero exit here is itself
informative, not just a launch-script bug.

## Owed

* The Mac verification transcript above (compile+count only; the gate
  had not cleared when this report was written — filled in this lane's
  final commit before hand-back, or by the manager/a follow-up agent if
  the gate outlives the lane).
* Posting "I-81 logs fetched" to pcrec-bench's inbox (this lane cannot
  write there; the manager should send it once the logs in this lane's
  scratchpad/commit are no longer needed on ubuntubudu's `out/`).
* The a+b·k entry-cost fit and the `PCREC_MIN_SCAN_CHAIN` gap decision
  themselves — out of this triage lane's scope (I-57: "report, never
  diagnose"; this lane's brief is the harness, not the measurement).
