# The validation-chain profile ([TT-5] stage 1, 2026-08-23)

Read-only pass: existing timestamped logs in `build/` plus the drivers'
source (Makefile, `tests/mech/run_sabotage_matrix.sh`, `tests/lib/
gen_timeout.sh`, `tests/bench/run_bench.sh`, `tests/bench/compare/gate.sh`).
No `make`, no test scripts, no benchmarks were run to produce this file — a
sibling lane was timing `make test` on this box while this pass ran. Every
number below is either read directly from a log/script or computed by
arithmetic on numbers read directly; anything else is named as a blind spot
in §5, not guessed.

**Disclosure per the brief's own instruction**: this session was spawned
with the repo's root `CLAUDE.md` and the manager's memory index injected as
context. The committed docs win over anything in the brief where they
conflict — one conflict was found and is called out inline in §4a and §4e
below (the brief's "read SAN-1's stated REASONS the ubsan/asan axes are
separate" turns out to be about TSan, not about ASan-vs-UBSan; and the
brief's "the gate needs load < 0.5" conflates two different thresholds that
the scripts define differently — both corrected in place, sourced, below).

---

## 1. The chain as run

### 1a. Battery stage wall times, three logged runs (trend, not one sample)

All three logs carry per-stage `START`/`EXIT` timestamps (added to the
ad hoc battery driver at some point between `build/battery_m62close.log`
[2026-08-21, no timestamps, `== STAGE test starting ==` only] and
`build/battery_m64.log` [2026-08-22, full timestamps] — see §5 for why "ad
hoc": no committed script produces these logs, see below). Durations below
are computed directly from each log's own `START`/`EXIT` lines.

| Stage | m64 (69f3b93, 12:58) | m64fix (8e4af41, 14:21, same day) | m65 (3aa446f, 20:59) |
|---|---|---|---|
| test | 10m04s | 9m59s | 10m14s |
| strict | 6s | 6s | 6s |
| ubsan | 27m20s | 27m46s | **32m35s** |
| asan | 34m18s | 36m07s | **42m25s** |
| lint | 31s | 30s | 33s |
| **battery total** | **1h12m19s** | **1h14m28s** | **1h25m53s** |

Sources: `build/battery_m64.log` lines 1,2714,2715,2717,2718,5027,5028,7337,
7338,7686; `build/battery_m64fix.log` lines 1,2702,2703,2705,2706,4979,4980,
7253,7254,7602; `build/battery_m65.log` lines 1,2749,2750,2752,2753,5099,
5100,7446,7447,7795.

**The trend, not just the m65 snapshot the brief quoted**: ubsan grew
27m20s→27m46s→32m35s and asan grew 34m18s→36m07s→42m25s across three
same-week runs — a +19% ubsan / +24% asan jump in the single day between
`m64fix` (14:21) and `m65` (20:59), the day module `backrefs` ([M6.5.2])
landed nineteen new sabotage rows and several new differential suites
(`brefdiff`, `dupnamesdiff`, `run_backref_identity.sh` — see
`tests/mech/run_sabotage_matrix.sh`'s suite-vocabulary comment, lines
54-70). The asan-minus-ubsan gap is ALSO growing on its own axis: 6m58s
(m64) → 8m21s (m64fix) → 9m50s (m65) — ASan's per-access instrumentation
scales worse with corpus growth than UBSan's does, on this workload. This
matters for §4a's arithmetic below: whatever a combined axis costs, it
should be measured against the CURRENT (m65) numbers, not the batteries a
week old, because the gap it would need to absorb is itself moving.

Two earlier logs, `build/battery_union2.log` and `build/battery_m62close.log`
(2026-08-21), carry the same `STAGE ... START/EXIT`-shaped section markers
(`STAGE test starting` / `STAGE strict starting` / ... / `BATTERY COMPLETE`)
but NO timestamps at all — confirms the marker shape is stable across at
least four runs (structural cross-check) but contributes nothing to the wall
-time trend; timestamping was added to the ad hoc driver sometime between
2026-08-21 and 2026-08-22's `m64` run.

**No committed script produces `battery_*.log`.** `grep -rn "BATTERY START"
scripts/ Makefile tests/` and a repo-wide `grep -rl "STAGE test START"
--include='*.sh'` both come back empty. The `== BATTERY START ...==` / `==
STAGE <name> START/EXIT ...==` lines are printed by whatever ad hoc shell
the manager types at the start of a battery run, not by a checked-in
harness — see §5.

### 1b. mech, and the total chain

`build/mech_m65.log`: `== MECH START 2026-08-22T22:25:56` →
`== MECH EXIT=0 2026-08-22T23:26:04` = **60m08s**, 118 rows, `0 anomalies, 2
undetected`. Matches `docs/dev/plan.md:339`'s figure exactly.

`build/mech_m64.log` (per `docs/dev/dev_journal.md:11891`): 15:36→16:26 =
**50m00s**, 99 rows (S88-S101 incl., journal:11888). No mech run is on
record specifically for `m64fix` (a same-day fix-round battery; mech was not
re-run for it — see the journal's part-12 entry).

**Total chain, two data points**:

| | battery | mech | total | rows |
|---|---|---|---|---|
| m64 (2026-08-22 12:58) | 1h12m19s | 50m00s | **2h02m19s** | 99 |
| m65 (2026-08-22 20:59 → 23:26) | 1h25m53s | 60m08s | **2h26m01s** | 118 |

This cross-checks `docs/dev/plan.md:337`'s "~2.5 h" for m65 (2h26m rounds to
that) and shows the chain grew ~24 minutes (+20%) in one day, tracking the
module landing that added 19 rows and several new differential suites —
the SAME cause visible in §1a's ubsan/asan growth. The chain is not merely
"slow"; it is growing at a rate proportional to how many new suites get
their own arm, and neither axis (battery or mech) currently has a growth
alarm the way `make test`'s own sections do (§4g).

**Not measured in either log**: the quiet-box performance gate
(`tests/bench/compare/gate.sh`) and the D27 blinded-corpus acceptance run,
both part of the merge chain per the brief's own framing and per
`docs/dev/wake.md:55-56` ("battery ... ≈85 min; `PROCS=4 make mech` ≈60
min" — no gate/D27 minutes given there either). No `build/gate_m65*.log`
or D27-run log with a timestamp exists yet for this HEAD as of this pass —
consistent with the journal's part-12 entry, which says the close "waits
on [lane/brfix] and on the gate." `tests/bench/CLAUDE.md:40` describes
`compare/gate.sh`'s underlying `compare.sh` only as "Slow (tens of
minutes)" — no number. This is a real gap in "the chain as run": the
profiled ~2.5h is the battery+mech portion only, and the brief's own
framing ("plus the quiet-box performance gate and a D27 blinded-corpus
acceptance run") implies the real per-merge total is higher by an
unmeasured amount. Named as a blind spot in §5.

---

## 2. Inside each stage

### 2a. `test`, `ubsan`, `asan`: the timestamp ceiling

The battery logs carry exactly ONE timestamp pair per stage (`STAGE <name>
START ...` / `STAGE <name> EXIT=0 ...`) and nothing finer inside. Every line
between those two markers is unstamped script output — section banners
(`bash tests/parse/run_parse_tests.sh`, `== run_group[N]: bash
tests/codegen/... ==`) and per-script `checks passed:`/`checks failed:`
summaries, but no `date`, no `real`/`user`/`sys`, no elapsed-seconds line
anywhere inside a stage. **A true section-by-section wall table cannot be
extracted from these logs — this is stated precisely rather than
approximated with a line-count proxy, which would misrepresent noise-heavy
scripts (e.g. the `mrldiff`/`counterkdiff` cell-count summaries) as
disproportionately expensive relative to quiet, slow ones (`test-corpus`'s
per-case output is terse).** What follows is what CAN be recovered from the
log plus the drivers' own source, not a substitute wall table.

**What the `test` stage actually runs today** (`Makefile:118-122`, the real
`test:` prerequisite list, 22 section targets — more than the 9-script/12-
section shape `docs/testing.md`'s "Tiered testing" section documents in
detail, which is dated 2026-08-13 and pre-dates modules `atomic-groups`,
`backrefs`, `prefilter`, `altcls`, `rungselect`, `counterk`, `mrl`,
`resource`, `capturediff`): `test-corpus test-cli test-reject test-registry
test-parse test-gentimeout test-codegen test-vm test-possessify
test-rungselect test-counterk test-mrl test-prefilter test-altcls
test-assertions test-atomic test-backrefs test-encseam test-resource
test-capturediff test-known-fail test-thread`. The per-section runtime
table in `docs/testing.md:727-745` is stale by this same margin (nine of
today's 22 sections did not exist when it was measured) — its own
"RE-RECORD TRIGGER" (`docs/testing.md:774-778`, re-measure when a section's
runtime doubles) has never fired because the table was never re-measured
against the current section list to know whether it should. This is exactly
what [TT-4.1]'s per-invocation-type census (already chartered, in progress —
`docs/dev/plan.md:314-321`) will produce as a side effect; not duplicated
here.

**What `ubsan`/`asan` run, ordered, from the Makefile** (`Makefile:602-628`
for ubsan, `Makefile:656-681` for asan — the two `for s in ...` lists are
IDENTICAL, 26 scripts): `tests/harness/run.sh, tests/cli/
run_cli_tests.sh, tests/reject/run_reject_tests.sh, tests/registry/
run_registry_tests.sh, tests/parse/run_parse_tests.sh, tests/codegen/
run_codegen_tests.sh, run_trie_identity.sh, run_endvar_identity.sh,
run_wordctx_identity.sh, run_mlinectx_identity.sh, run_gstart_identity.sh,
run_vm_identity.sh, run_ir_listing.sh, tests/vm/run_vm_tests.sh, tests/
encseam/run_encseam_tests.sh, tests/possessify/run_possdiff.sh,
run_possessify_tests.sh, tests/rungselect/run_rungdiff.sh,
run_rungselect_tests.sh, tests/altcls/run_altdiff.sh, run_altcls_tests.sh,
tests/assertions/run_assertions_tests.sh, tests/atomic_groups/
run_atomic_diff.sh, tests/backrefs/run_backref_diff.sh,
run_dupnames_diff.sh, tests/lib/run_gen_timeout_tests.sh, tests/
known_fail/run_known_fail.sh`.

**A genuine coverage gap, found while comparing this list against `test:`'s
own** (not asked for by the brief, but directly relevant to §3's redundancy
arithmetic — if ubsan/asan re-ran literally everything `test` does, the
"twice over" estimate would be simpler than it is): the sanitizer axes do
**NOT** run `tests/mrl/run_mrldiff.sh`, `tests/counterk/
run_counterkdiff.sh`, `tests/prefilter/run_prefilter_tests.sh`, `tests/
resource/run_resource_tests.sh`, `tests/fuzz/run_capturediff_gate.sh`,
`tests/assertions/run_mline_diff.sh`, `tests/assertions/run_gstart_diff.sh`,
`tests/mrl/run_mrl_tests.sh`, `tests/thread/*` (thread is a deliberate
exclusion, `Makefile:576-582`/`docs/testing.md:1723-1731` — the others are
not called out anywhere as deliberate). So "the sanitizer axes re-run the
whole suite" (the brief's framing, and this document's own §3) is
approximately but not exactly true: it is closer to 26 of `test:`'s
~30-odd scripts, not all of them. Whether the omission of `mrldiff` /
`counterkdiff` / `prefilter` / `resource` / `capturediff` / `mline_diff` /
`gstart_diff` from the compiler+compilee-axis sweep is a deliberate,
documented decision or a drift (these six sections postdate SAN-1's
2026-08-13 landing and its list may simply never have been revisited) is
not answered anywhere in `docs/testing.md` or `docs/dev/decisions.md` —
named as a blind spot in §5, separate from [TT-5]'s own scope.

### 2b. mech: no per-row timestamps — the stated blind spot, characterized by kind instead

`build/mech_m65.log` has 118 `-- running S<NN>_*.sh --` lines and nothing
else timestamped between `MECH START` and `MECH EXIT` (verified: `grep -n
"^-- running\|START\|EXIT" build/mech_m65.log` — the two bracketing lines
are the only timestamps in the file). **Per-row wall time is not
recoverable from the log at all.** What follows instead is the cost model
`run_sabotage_matrix.sh`'s own source gives directly.

**What one row costs, by KIND** (`tests/mech/run_sabotage_matrix.sh`,
`run_one()`, lines 189+): `git archive HEAD` into a fresh scratch tree,
verify the sabotage's `BEFORE`/`AFTER` text landed exactly `SAB_COUNT`
times (`tests/mech/lib/replace.py`), `make all` the sabotaged tree, then
run ONLY the suites its `SAB_SUITES` word list names (lines 290-745, one
`case "$suite" in ...)` arm per word) — never the full `make test`. The
**rebuild is cheap and NOT the dominant cost**: `tests/mech/CLAUDE.md:129-
130` measured it directly — `git archive HEAD` 0.04s, `make all -j12`
0.75s, on a 12-core box. What dominates is which suites a row's
`SAB_SUITES` names: the same file (line 131) measured `registry` 0.60s,
`pc3` 4.36s, `cli` 5.46s against the `reject` arm's **54.75s** — a ~10-90x
spread between the cheapest and most expensive arms, all paid per-row on
top of the ~0.8s rebuild.

**Rows tabulated by target class** (counted directly from `tests/mech/
sabotages/*.sh`'s `SAB_SUITES=` lines, 118 files):

| class | count | cost signature |
|---|---|---|
| includes `harness` (runs `tests/harness/run.sh`, the `.rxt` corpus) | 62 / 118 | of these, **58 already pass `SAB_HARNESS_TARGET`** — a single named `.rxt` file, not the full corpus (`tests/mech/sabotages/*.sh`'s `SAB_HARNESS_TARGET=` lines; the `harness)` arm at `run_sabotage_matrix.sh:738-741` only widens to the full corpus when that var is unset) |
| `harness` with NO `SAB_HARNESS_TARGET` (full ~22K-case corpus) | **4 / 118** | `S59_mrl_minw_overreports.sh`, `S66_altcls_merge_drops_union.sh`, `S71_wordctx_alphabet_unconditional.sh`, `S76_mlinectx_alphabet_unconditional.sh` |
| includes `reject` (54.75s arm per the measured note above) | ~19 / 118 | `reject` alone (9), `reject registry pc3` (5), plus 5 more combinations |
| targeted differential/structural arms only, no `harness`, no `reject` | 56 / 118 | `codegen` (7), `codegen harness` (9, already counted above), `possdiff` (5), `counterkdiff` (5), `vm` (4), `trie` (3), and 13 more small groups |

**Finding, stated plainly because it cuts against the charter's assumption**
(`docs/dev/plan.md:352` names "mech per-row scoping (which sections a row
really needs)" as a candidate): **the obvious scoping win is already mostly
banked.** 58 of 62 `harness`-touching rows are already scoped to one file;
only 4 rows run the untargeted full corpus, and all four are recent
(post-2026-08-17 module rows, per their `S<NN>` numbers) rather than an
unaddressed backlog. The remaining scoping opportunity is narrower than
"which sections does a row need" — it is closer to "do those 4 rows need
the WHOLE corpus, or would their own module's `.rxt` directory suffice the
way the other 58 rows already do" (§4b).

**Per-row average, two data points, computed from §1b**: m64 — 50m00s /
99 rows = 30.3s/row wall (at PROCS=4, so ≈121.2 row-seconds of work per
row if perfectly parallelized). m65 — 60m08s / 118 rows = 30.6s/row wall
(≈122.4 row-seconds). Remarkably stable despite the suite growing by 19
rows and several new heavyweight differentials (`brefdiff`'s described
"5,808-cell sweep" per `tests/mech/CLAUDE.md`'s own note on the module) —
consistent with most new rows landing in the cheap `possdiff`/`counterkdiff`
/`trie`-shaped arms rather than the `harness`/`reject` ones, though this is
inferred from the tabulation above, not measured directly per row.

---

## 3. Redundancy map

1. **Baseline `test` + `ubsan` + `asan` each independently compile-and-run
   the same ~22,138-case corpus end to end** (`tests/harness/run.sh` is
   `test-corpus`'s script AND appears in both sanitizer lists —
   `Makefile:118`, `602`, `656`) — three full passes per merge, differing
   ONLY in the `GENCFLAGS`/compiler flags each axis carries, per SAN-1's
   own design (`docs/testing.md:1224-1245`: `GENCFLAGS` is a compile-flag
   hook layered onto whatever C `pcrec` already emitted — it does not
   change what `pcrec` emits). `pcrec`'s own invocation and the harness's
   per-case bookkeeping (mktemp, file writes) are therefore identical work
   repeated three times; only the `gcc`/link/run step legitimately differs
   per axis. This is candidate (d) below, and is the concrete substance
   behind the brief's "twice over" framing (which undercounts by one pass —
   it is baseline+ubsan+asan, three, not two).

2. **The four identity gates compile ~1,200 corpus patterns TWICE, ~2,400
   gcc calls** — already measured and cited verbatim in the TT-4 charter,
   `docs/dev/plan.md:279-284` (the assertions+identity-gates section, 458s
   at the time of that census). Not re-measured here; cited because it is
   the same SHAPE of redundancy as item 1, one level down (within a single
   `test` run, not across axes), and TT-4.1's per-invocation census will
   produce the current number.

3. **mech rebuilds pcrec from scratch once per sabotage** (118 times for
   m65) — but per §2b this is measured CHEAP (0.75s at `-j12`), so the
   redundancy that matters is not the rebuild, it is that **most of each
   fresh tree is byte-identical to the previous sabotage's** (`docs/
   testing.md:1861-1863`, TT-3's own framing: "most sabotages touch only
   1-2 source files ... most of a sabotage's ~27 objects are BYTE-
   IDENTICAL to the previous sabotage's"), which is exactly what CCACHE=1
   is measured to exploit for mech (candidate c) and NOT for `make test`
   (measured NO, `docs/testing.md:1768-1850`).

4. **The battery's `test` stage and mech's `harness`-class rows both run
   `tests/harness/run.sh` against the same tree** at merge time — once as
   part of the ~10-minute `test` stage (full corpus, unsabotaged), and
   again, on 62 SEPARATE sabotaged rebuilds, either against a scoped file
   (58 rows) or the full corpus (4 rows). This is not literally redundant
   (each row asks a different, sabotaged-code question) but it means the
   corpus harness's own per-case overhead (mktemp, `pcrec` invocation,
   `gcc` compile, run) is paid at least 63 times total per merge (1 clean +
   62 sabotaged) before counting `ubsan`/`asan`'s own corpus pass — the
   `test-corpus` shape alone is exercised roughly 65 times across one full
   chain.

5. **The gate (`tests/bench/compare/gate.sh`) and the standing `make bench`
   throughput cases both measure pcrec's own throughput** — `make bench`'s
   own cases are excluded from `make test`/`ubsan`/`asan`/mech entirely
   (`docs/testing.md:1731-1735`: "`bench`'s numbers are timing medians
   that sanitizer overhead would invalidate"), and are a SEPARATE
   standing target, not part of the profiled battery/mech chain at all —
   named here because the brief's chain description implies the gate is
   the only throughput check, when `make bench` (not sanitizer-safe,
   never touched by the battery) is a second, disjoint one. Not
   double-run in the sense of redundant work, since neither is part of
   the timed chain in §1, but worth naming so a reader does not conflate
   "the gate ran" with "throughput was checked once."

---

## 4. Candidate moves

Ranked informally by (estimated minutes saved) / (risk + effort); every
estimate below is explicitly flagged thin where it is.

### (a) One combined `-fsanitize=address,undefined` axis

**What it would save, from the numbers in §1a**: today's two axes cost
32m35s (ubsan) + 42m25s (asan) = **75m00s** combined (m65). Two rebuilds,
two full 26-script suite passes. A combined axis pays ONE rebuild and ONE
suite pass, at combined instrumentation cost.

**The brief's framing needs a correction, sourced from the Makefile
itself**: SAN-1's documented reason two axes exist is about **TSan**, not
about ASan-vs-UBSan. `Makefile:576-580` (comment directly above the
`ubsan:`/`asan:` targets): "TSan already lives in `tests/thread`
(`make test`); it is deliberately NOT re-run here — combining ASan/UBSan
instrumentation with an already-TSan'd build is not how sanitizers compose
on this toolchain." This explains why `tests/thread/` is excluded from
BOTH `ubsan` and `asan` (`docs/testing.md:1723-1731`); it says nothing
about combining ASan and UBSan WITH EACH OTHER, which is a routine,
well-supported gcc/clang combination in general (`-fsanitize=address,
undefined` compiling and linking together) — no documented reason in this
repo forbids it, because SAN-1 was never asked the question. **This is the
one place the brief's own framing and the committed docs disagree**, per
the disclosure at the top of this file; the committed Makefile comment is
what is cited above.

**What survives the merge, checked against the mechanisms that would need
to keep working**:
- `tests/lib/gen_timeout.sh`'s D45 budgets key off the LITERAL SUBSTRING
  `-fsanitize=` in the compile flags (`gen_timeout.sh:87,96,124,351` —
  `*-fsanitize=*)`), not which specific sanitizer. A combined
  `-fsanitize=address,undefined` flag still matches that glob, so the
  180s/60s sanitizer-axis budgets apply unchanged — no gen-timeout work
  needed.
- The battery's `lint` stage is untouched either way (separate target,
  `-fanalyzer`, no `-fsanitize` involvement at all).
- K26 (LeakSanitizer no-op on this box, `-fsanitize=address,leak` today,
  `Makefile:638`) is unaffected in principle — LSan rides with `address`
  regardless of whether `undefined` joins it — but this needs verifying
  on a real combined build, not assumed.
- `UBSAN_ENV`/`ASAN_ENV` (`Makefile:586-593`, `639-646`) set DIFFERENT
  `*_OPTIONS` env vars (`UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"`
  vs `ASAN_OPTIONS="detect_leaks=1"` + `LSAN_OPTIONS=""`) — both would need
  to be exported together for a merged run, unremarkable but a real wiring
  step, not zero-cost.

**Estimate**: no public/documented number for THIS codebase's combined-axis
overhead exists to cite — this is exactly what the brief asks to flag as
thin. If the combined run costs roughly "ASan alone plus a modest
UBSan-on-top delta" (a common real-world pattern, not measured here), a
plausible range is ~45-55 minutes for the single pass, saving **~20-30
minutes per merge (~27-40% of the current 75-minute sanitizer budget, ~14-
20% of the whole ~146-minute chain)**. This number is a hypothesis, not a
measurement, and MUST be measured on a real combined build (two
`BUILD_DIR`s merged into one, `SAN_CFLAGS := -O1 -g -fsanitize=address,
undefined,leak -fno-sanitize-recover=undefined`, one `SAN_ENV` union)
before it becomes a row — same discipline TT-3 used, and the same
discipline that refuted TT-3's own charter prediction. **Rank: highest of
the six — largest absolute number, and no documented reason blocks it; the
"reason to check first" the brief pointed at turned out to be about a
different pair of sanitizers.**

### (b) mech per-row scoping

Per §2b, the "obvious" win (scope `harness` rows to one file) is already
58/62 done. What remains, each needing its own measurement:

- **The 4 full-corpus `harness` rows** (`S59`, `S66`, `S71`, `S76`) each
  belong to a specific module (`mrl`, `altcls`, `wordctx`, `mlinectx`
  respectively, by name) that already has its OWN `.rxt` directory the
  other 58 rows point `SAB_HARNESS_TARGET` at. Scoping these four the same
  way would save whatever the full-corpus-minus-one-file delta is on
  those four rows specifically — not measured here, but bounded above by
  `docs/testing.md:727`'s dated `test-corpus` figure (303s serial in
  2026-08-13; the corpus has grown roughly 15x since — 1,270 cases then
  per that section vs 22,138 now per `docs/dev/wake.md:42` — so the CURRENT
  full-corpus cost per row is unknown and itself needs measuring before
  this saving can be sized).
- **PROCS=4 for mech's row-level concurrency was set from a measurement on
  a 20-sabotage matrix, 2026-08-12** (`docs/dev/dev_journal.md:6206-6208`:
  "6m20s serial → 1m57s at PROCS=4" — the ORIGIN of the default), never
  re-measured against the current 118-row matrix or against higher PROCS
  on this box's 12 cores. `docs/dev/wake.md:56` still quotes "`PROCS=4
  make mech` ≈ 60 min" as the standing figure, six weeks and ~6x the row
  count later.
- **A real oversubscription risk, found reading the dispatch code rather
  than asserted**: `run_sabotage_matrix.sh`'s `PROCS` variable controls
  ROW-level concurrency and derives `JOBS` (build parallelism per tree,
  `nproc/PROCS`, lines 121-126) — but the suite arms it calls per row
  (`reject)` at line ~721, `harness)` at line ~738) invoke `tests/reject/
  run_reject_tests.sh` and `tests/harness/run.sh` WITHOUT overriding
  `PROCS` in their own environment. Both of those scripts read `PROCS`
  from the environment directly to decide their OWN internal worker count
  (`docs/testing.md:1063-1080` for reject's call-index sharding,
  `:1188-1198` for harness's pre-existing mechanism) — and since
  `run_sabotage_matrix.sh` itself runs under `PROCS=${PROCS:-$(nproc)}`
  (`Makefile:727`, i.e. `PROCS=4` for the m65 mech run, exported into the
  shell's environment), that same `PROCS=4` is visible to every child
  process the script forks unless something clears it. If it is not
  cleared, up to 4 concurrently-running rows that each hit `reject` or
  `harness` would EACH additionally shard into 4 internal workers — up to
  16 concurrent heavy processes on a 12-core box, the same oversubscription
  shape `docs/testing.md:1157-1166` already documents and measures for
  `make -j$(nproc) -Otarget test`'s OWN internal-fan-out-plus-section-
  concurrency case (and offers `PROCS=1 make -j$(nproc) -Otarget test` as
  the fix there). **Whether this actually happens (vs. the environment
  somehow not propagating, or the two concurrency levels netting out
  fine on this box's core count) is not verified by this read-only pass**
  — it would take one instrumented row confirming a child's `$PROCS`
  value, or a `ps`/`nproc`-count sample taken during a live `PROCS=4 make
  mech` run. Named precisely because it could cut either way: if real, an
  explicit `PROCS=1` on the two suite-arm invocations inside `run_one`
  would REMOVE oversubscription (a speed gain from LESS internal
  parallelism, counter-intuitively); if not real, PROCS could plausibly
  go higher than 4 with room to spare.

**Estimate**: too dependent on the two open measurements above to size
honestly. If the oversubscription risk is real and fixing it lets PROCS
rise from 4 toward 8-12 cleanly, the mech stage's ~60 minutes could
plausibly fall by a large fraction (mech is close to embarrassingly
parallel — 118 independent rows) — but this is speculative pending the one
measurement named. **Rank: second — the fix is cheap to try (one line) and
the failure mode (oversubscription silently eating the PROCS=4 win) is a
real, specific, citable risk, not a vague "maybe parallelize more."**

### (c) CCACHE=1 for mech

Already measured and ruled a **qualified YES**, not proposed fresh here —
`docs/testing.md:1850-1888` ("One mech row: cold/warm/plain, measured"):
S26 (heavier row, `SAB_SUITES="harness"`) 25% faster warm (6.69s plain →
5.00s warm); S01 (lighter, `codegen` only) 29% faster warm (5.53s → 3.91s).
Both are WITHIN-SABOTAGE repeats (same sabotage run twice), explicitly
flagged as a weaker signal than the real production case (118 DIFFERENT
sabotages back to back, most touching 1-2 of ~27 files — cross-sabotage
reuse "should be even higher... stated above rather than assumed
silently," same section). **What it would need measured before becoming a
row, verbatim from the doc that already ruled on this**: "the FULL
~50-minute matrix cold/warm (out of this row's time budget) — the two
single-row samples are the evidence on record."

**Estimate, from the numbers already on file**: if 25-29% held across the
full m65 matrix (60m08s), that is **~15-17 minutes saved per merge** — a
real number IF cross-sabotage reuse is at least as good as the two
single-row samples, which is plausible but, per the doc's own words, not
proven. `docs/testing.md:1913-1921` ("Disposition") already notes the
wiring is correct and the toggle is opt-in and safe; merging it for mech
specifically (leaving `make test` alone, per its own decisive NO) is a
manager call the doc explicitly declines to make. **Rank: third — the
smallest of the sized candidates, but the ONLY one with real measured
data behind its estimate rather than a hypothesis, and zero new
engineering (the wiring already exists and is proven byte-identical when
off).**

### (d) A shared set of generated `.c` artifacts across the sanitizer axes

Per §3 item 1: `pcrec`'s emitted C for a given pattern does not depend on
`GENCFLAGS` (SAN-1's own premise, `docs/testing.md:1224-1245` — the hook is
a compile-flag layer, not a `pcrec` input) or on which axis is running.
So, in principle, `pcrec`'s ~22,138 invocations and the harness's per-case
orchestration (mktemp, write, dispatch) could run ONCE, with the resulting
`.c` files reused by `test`, `ubsan`, and `asan`'s three separate `gcc`
compile+link+run passes — each axis would still pay its own full
compile+link+run (that step legitimately differs), but would stop paying
`pcrec`+harness-bookkeeping three times over.

**How much of an axis's wall this actually is: NOT KNOWN from this pass,
and NOT independently derivable** — this is precisely the split [TT-4.1]
is already chartered to measure (`docs/dev/plan.md:314-321`: "Census over
one `make test` by section ... invocation counts (pcrec, gcc one-shot, gcc
-c, link) and wall time split pcrec / gcc / link / run / harness-
overhead"), and that lane is running concurrently with this one per the
brief's own instruction not to duplicate it. **This candidate should be
evaluated using TT-4.1's numbers once they land, not re-measured here.**
Note also that this is a DIFFERENT axis of sharing than [TT-4]'s own
charter, which is explicitly scoped to "batching at the gcc/link step
ONLY: per-pattern `.c` artifacts keep existing" (`docs/dev/plan.md:295-
296`) — TT-4 batches MANY patterns into one `gcc` call within a single
axis; this candidate shares ONE pattern's `.c` file ACROSS axes. The two
are complementary, not overlapping, and could in principle stack (share
across axes, then batch within each axis's compile step) — an increment
this document surfaces but does not size.

**Rank: unranked pending TT-4.1** — plausibly large (three-way repeated
harness overhead is not free), but sizing it now would mean guessing the
exact number the sibling lane is already producing.

### (e) Pipelining stages on a quiet box

**Correction to the brief's framing, sourced from two DIFFERENT
thresholds that are easy to conflate**: `docs/dev/wake.md:62` (uncommitted,
"committed docs win on any disagreement" — `docs/dev/CLAUDE.md`'s own rule
for this exact file) states the OPERATING DISCIPLINE as "quiet-box gate
(load < 0.5)" — a human precondition: do not START the gate until the box
looks idle, for a trustworthy measurement. Separately, `tests/bench/
run_bench.sh:279-286` defines the SCRIPT'S OWN internal `LOAD_LIMIT` as
`max(2.0, nproc*0.5)` — 6.0 on this 12-core box (confirmed at line 165's
comment: "LOAD_LIMIT 6.0") — the threshold at which a budget MISS gets
downgraded from FAIL to INCONCLUSIVE rather than treated as a real
regression. These are not the same number and answer different questions:
0.5 is "is the box quiet enough to trust a run I am about to start," 6.0
is "how loaded can the box get mid-run before I stop trusting a bad
result." Both point the same direction for this candidate, though: the
gate wants the box substantially idle (well under half its 12 cores busy)
to produce numbers worth trusting at all, whichever threshold is applied.

**Which stages are CPU-bound**: `test`'s heaviest sections (`test-corpus`,
`test-reject`) and BOTH sanitizer axes default `PROCS`/`GROUP_PROCS` to
`nproc` (`Makefile:135`,`151`,`592`,`646` etc. — every `PROCS=$${PROCS:-
$$(nproc)}` site) — i.e. `ubsan` and `asan` EACH already try to use all 12
cores internally when run alone. `strict` is a single `-Werror` compile
pass (~6s, effectively single-threaded serial by comparison). `lint`
(`gcc -fanalyzer`, ~30s) is comparably light. mech runs at `PROCS=4` by
policy (§4b). So the two heavy stages (ubsan, asan) are ALREADY
core-saturating on their own — running them concurrently with each other
would need explicit `PROCS` capping on each (e.g. `PROCS=6` apiece) to
avoid the SAME oversubscription risk named in §4b, and the resulting wall
-time win is not guaranteed positive without measuring it (this is the
same "obvious idea measured as a slowdown" trap TT-3's own charter warns
about, `docs/dev/plan.md:277-278`'s cited lesson). `strict` and `lint`
(cheap, mostly-serial) are the only genuinely free overlap candidates —
together they cost under a minute of the ~2.5h chain, so overlapping them
with anything else saves well under 1% of the total.

**Estimate**: essentially unsized — the one overlap that is clearly safe
(`strict`+`lint` against something else) is too cheap to matter; the one
overlap that would matter (ubsan+asan concurrently, each capped) needs the
same kind of before/after measurement as (a) and (b), and risks
oversubscription for an unknown net gain. **Rank: lowest of the sized
candidates — real CPU headroom exists only during the light stages, which
are not the stages costing minutes.**

### (f) Change-scoped chains for test-infrastructure-only or docs-only changes

**No codified merge-bar rule distinguishing docs-only changes was found**
in `docs/testing.md` or `docs/dev/decisions.md` (searched for "docs-only",
"documentation-only", "merge bar", "full battery" — the only "full
battery" hit, `docs/dev/decisions.md:3846`, is unrelated context). What
exists instead is INFORMAL PRECEDENT: several journal entries record
docs-only merges proceeding without a logged battery run at all —
`docs/dev/dev_journal.md:8326` ("Corpus counts unchanged (all four merges
docs-only — no src/ or tests/ ...)"), `:9319` ("K23 NOTE MERGED ...,
docs-only, conflict in ..."), `:11517` ("Merged docs-only (no src/lib/cli/
tests/Makefile delta on the branch)"). None of these three cites a battery
run in the surrounding text, which is consistent with an unwritten
practice of skipping the full chain for changes that touch no `src/`,
`tests/`, `lib/`, `cli/`, or `Makefile` path — but it is precedent, not a
rule, and nothing enforces it (a docs-only PR is not gated one way or the
other today; the practice depends on whoever is merging remembering it).

**What this candidate actually is, then**: not a new mechanism, but
CODIFYING the existing informal practice as an explicit, checked
rule — e.g. a merge-time check on `git diff --name-only` against the base
that skips the battery/mech chain (or downgrades it to `make smoke`) when
the touched-path set is empty of `src/`, `tests/`, `lib/`, `cli/`,
`Makefile`, `scripts/`. This would save the FULL chain (~2.5h+) on
docs-only changes, which per the three journal citations above are not
rare. **Risk**: getting the touched-path predicate wrong once (e.g.
missing that a "docs" change also touched a `.rxt` file, or a script under
`scripts/`) would silently under-test a real change — the same class of
risk `docs/testing.md`'s touched-path table (§"Touched-path → sections")
already carries and is explicit is "guidance... not a substitute for full
load" (`docs/testing.md:779`). **Rank: cheap and low-risk if scoped
narrowly (docs/ only, nothing else) and paired with a hard fallback (any
ambiguity → full chain), but the win only applies to a subset of merges,
not the recurring cost the brief is chartered against** (module landings,
which are the chain's actual growth driver per §1, are never docs-only).

### (g) Suggested by the numbers, not on the brief's list: a growth alarm for the battery and mech, mirroring `make test`'s own

`docs/testing.md`'s "Tiered testing" section already has exactly this
mechanism for `make test`'s sections: "RE-RECORD TRIGGER: re-measure a
section ... whenever its runtime doubles from the figures above"
(`docs/testing.md:774-778`). Nothing equivalent exists for `ubsan`/`asan`/
mech — and §1's own trend data shows they need it MORE, not less: ubsan
+19%, asan +24%, mech's total chain +20%, all in the single day between
`m64fix` and `m65`, driven by one module landing. At that rate, three or
four more module landings compound the ~2.5h chain toward 4+ hours with
no instrumented signal that it is happening beyond someone noticing the
wall clock feels longer — which is exactly the complaint that chartered
[TT-5] in the first place (`docs/dev/plan.md:332-336`, quoting Frank: "we
are in the multiple hours for overall testing right now"). A cheap,
low-risk row: extend the ad hoc battery driver (or, better, commit it —
see §5) to log its own stage durations against a pinned reference (the
three numbers in §1a's table) and flag when any stage exceeds some
multiple of its own history, the same discipline already proven for
`make test`. **Not sized** — this is a process/alarm candidate, not a
time-saving one, so "minutes saved" does not apply; its value is catching
the NEXT doubling before someone has to charter a second [TT-5].

---

## 5. Blind spots

| Blind spot | One-line measurement that would settle it |
|---|---|
| No section-level (script-level) timestamps exist inside `test`/`ubsan`/`asan` stages (§2a) | Add a `date`/`SECONDS`-delta print around each `bash tests/...` invocation in whatever drives the next battery run — a few lines, one run to get the first real section table |
| No committed script produces the `battery_*.log`/`STAGE ... START/EXIT` shape at all (§1a) | `git log --all -- '*battery*'` / ask whoever runs it where the shell lives, and commit it under `scripts/` (this would also directly enable the above) |
| No per-row timestamps in mech's log, and the PROCS-inheritance oversubscription risk (§2b, §4b) is read from source, not observed live | One instrumented `PROCS=4 make mech` run with `date` bracketing each `run_one` call, or a `ps`-sample during a live run to count concurrent `reject`/`harness` worker processes |
| PROCS=4 for mech was measured once on a 20-row matrix six weeks before the current 118-row one (§4b) | Re-run the same `PROCS` sweep (`1, 4, 8, 12`) `dev_journal.md:6206-6208` did originally, on the current matrix |
| The quiet-box gate and D27 acceptance run's wall time is absent from every log checked (§1b) | Time the next gate run and D27 run explicitly (`time bash tests/bench/compare/gate.sh`, similarly for the D27 driver) and log it the way the battery already does |
| Combined-axis (`-fsanitize=address,undefined`) overhead on THIS codebase, THIS gcc (§4a) | Build one probe target with the combined flag set over a representative subset (or the full suite) and compare wall time against today's 75-minute two-axis figure |
| Whether the 6 differential scripts missing from the sanitizer axes' lists (§2a) are a deliberate exclusion or drift | Check `docs/dev/decisions.md`/git blame on `Makefile`'s `ubsan:`/`asan:` targets for when each script's line was (or wasn't) added relative to its module landing |
| How much of an axis's wall is `pcrec`-invocation-plus-harness-overhead vs. `gcc`/link/run (§4d) | [TT-4.1]'s own census, already in flight — read its output when it lands rather than re-deriving here |
| Whether docs-only merges in the journal (§4f) actually skipped the battery, or just didn't mention it | `git log` those three commits' surrounding history for a battery-log reference, or ask whoever merged them |

---

## Sources consulted

`build/battery_m64.log`, `build/battery_m64fix.log`, `build/battery_m65.log`,
`build/battery_union2.log`, `build/battery_m62close.log`,
`build/mech_m64.log` (referenced via journal), `build/mech_m65.log`,
`build/gate_m62close.log`; `Makefile`; `tests/mech/run_sabotage_matrix.sh`;
`tests/mech/CLAUDE.md`; `tests/mech/sabotages/*.sh` (118 files, `SAB_SUITES`/
`SAB_HARNESS_TARGET` tabulated directly); `tests/lib/gen_timeout.sh`;
`tests/bench/run_bench.sh`; `tests/bench/compare/gate.sh`; `tests/bench/
CLAUDE.md`; `docs/testing.md` ("Tiered testing", "Internal parallelism and
section composition", "Sanitizer + lint battery", "Battery integration —
DECIDED", "Compile caching"); `docs/dev/plan.md` ([TT-4], [TT-5]);
`docs/dev/plan_completed.md` ([TT-1], [TT-2], [TT-3], [SAN-1]);
`docs/dev/dev_journal.md` (PROCS=4 origin, m64/m65 battery+mech entries);
`docs/dev/wake.md`; `docs/dev/CLAUDE.md`.
