# lim2 report — [LIM-2] the DFA route's projected-size bail

Lane `lim2`, worktree `worktrees/lim2`, branch `lane/lim2`, from `main` at
`56f34b01` (abi 20). **Status (post-`.lift`, 2026-09-04): the census is
built and run, and it is RED for a real, reported reason (§10). A real
`--engine=auto` regression the census's own `make test` run surfaced was
found and fixed (§11) — the write phase's own acceptance bar ("the
refusal set moves NOT AT ALL") was violated by the delivered code before
this fix.** Sections 1-8 below are the write-phase report, kept verbatim
except where a post-lift finding corrects one of its claims (marked
inline); §9 records what the post-lift sequencing actually found, in
order.

Disclosure (scope mandate): the only injected context that shaped a
decision was the repo `CLAUDE.md` (the situation-index table's rows on
`gnutimeout`/`scripts/watchdog`, the "change anything a caller can observe
→ spec hunk" row, and the general-mechanisms/D77 memory pointers) and the
memory index summaries named in the brief. Nothing else outside the brief
and the charter's own named files influenced the design.

## 1. Where the projection lives, and why the charter's own premise needed revising

**The charter's premise, checked first.** `PCREC_MAX_TABLE_ENTRIES`
(2,000,000 entries, "≈12 MB source") already bounds subset construction's
OWN state cap, and is far above `PCREC_MAX_EMIT_BYTES` (1,000,000 *bytes*,
not entries) — so construction routinely runs to ~150,000+ entries before
the emit-bytes cap would ever have accepted the result. That gap is real
and is exactly [LIM-2]'s target.

**The projection itself lives in `src/ir/dfa.c`'s worklist loop**
(`pcrec_build_dfa`), the same loop that already interns states via
`make_state` and already refuses mid-construction for the state-count and
K7 (`PCREC_MAX_SUBSET_ELEMS`) caps — this is the established idiom for a
during-construction refusal in this file, not a new one. Per finalized
state row (`si`, all `ncls` classes decided), it adds that row's EXACT
text-byte contribution to a running total, using the same nested order and
`" %d,"`/`"\n       "`-every-16-cells layout `src/gen/emit_dfa.c`'s
`emit_tr_table` uses — computed by digit-count arithmetic, never by
building the string.

**It is scoped to ONE call site**: the mandatory forward table-engine
build (`compile.c`'s `cx.job->dfa`), via a new `size_bail` parameter on
`pcrec_build_dfa` (four call sites total; only this one passes `true`).
Not the reverse machine, not the ENG_ATTEMPT/goto engine, not the anchored
machine — see §2 for why forward-only is the sound choice, not just the
convenient one.

**Representation certainty, not a guess.** The projection assumes the
INDEXED table form (`cell_type "short"`, `cell_of(st) = st`) and only acts
once `d->n * d->ncls > PREMUL_MAX_ENTRIES` (65,535) — at which point
`emit_dfa.c`'s `dfa_premul` is PROVABLY false for the rest of this
machine's life (its first conjunct, `ents > PREMUL_MAX_ENTRIES`, is
independent of any deny flag or seed condition), so indexed is the
guaranteed final form for every row counted, including rows decided
before the threshold crossed. `PREMUL_DEAD`/`PREMUL_MAX_ENTRIES` moved
from `emit_dfa.c` to `src/core/internal.h` so both files read one symbol
— this project's own stated anti-pattern is "two literals that must be
kept in step," and duplicating 65535 would have been exactly that.

## 2. What is exact, what is bounded, and the correctness finding that reshaped the design

**What's exact:** the cell-text-byte formula itself (an arithmetic mirror
of `emit_tr_table`'s own loop), and — new since the charter's own framing
— the REVERSE machine's contribution, once it is finished and minimized
(see §3).

**What is NOT exact, and the reason the charter's "states × classes × cell
width is exact" premise needed a correction:** the projection runs DURING
RAW subset construction, but `src/opt/minimize.c` runs AFTER
`pcrec_build_dfa` returns and only ever REMOVES states. Measured on the
worktree's own instrumented build (temporary debug prints, removed before
this diff — not part of the delivered patch):

| witness | raw fwd n | minimized fwd n | fwd shrink | raw rev n | minimized rev n | rev shrink |
|---|---|---|---|---|---|---|
| `w-2048` (altwide) | 9,872 | 9,798 | 0.75% | 9,817 | 6,925 | 29.5% |
| `s-4096` (altwide) | 8,269 | 7,976 | 3.5% | 8,104 | 2,806 | 65.4% |

So a raw-construction byte count is **not** a rigorous lower bound on the
machine's own final (minimized) table bytes — it can overstate it, on the
REVERSE machine substantially. This is why the projection is scoped to
the FORWARD machine only (its own shrink measured small, ≤3.5%, on both
witnesses that actually reach the expensive population) and why it
carries a margin (`BAIL_KEEP_PCT`, §4) rather than triggering on the raw
figure directly. **This is a real, disclosed gap between "exact" as the
charter framed it and what is actually provable without finishing
minimization** — flagged for ruling in §7.

## 3. The reverse-headstart redesign (why a naive forward-only bail was not enough)

The first working version (forward-only, no headstart, a `2×cap` margin)
built and ran, but **did not fire** on `w-2048` — it fell through to the
old post-emission check, unchanged, 10.97s. Measured cause: the forward
table alone is only **~60% of the total artifact** (1,427,829 of
2,379,410 bytes on `w-2048`'s full, uncapped artifact) — so even a raw
forward-only projection with no margin at all could only ever reach
`cap` once forward's own bytes hit `cap`, which for this witness is ~70%
of the way through forward's own growth (and construction time, measured
separately, correlates closely with rows processed — not front-loaded as
first hypothesized).

**Fix**: `compile.c`'s D7 fast path now builds and MINIMIZES the reverse
machine FIRST (reverse construction is cheap regardless — 23-24ms on both
big witnesses, against 10.68s and 19.45s for forward). Its exact,
already-minimized table byte count (`pcrec_dfa_indexed_table_bytes`, a new
small helper, same formula, run once over a finished machine) is passed
into the forward build as `size_bail_headstart`, shrinking the forward
budget needed before the bail can prove anything. This reorder is argued
order-independent for every other observable in `compile.c`'s own comment
at the site (K7's running total is order-independent by construction;
each machine's own state cap is a separate field; no refusal names a
machine) — and is EMPIRICALLY confirmed order-independent below (§5,
byte-identity on accepted patterns; verdict parity on refused ones).

## 4. The margin (`BAIL_KEEP_PCT = 85`) — a judgment call, not a proof

Refuse once `size_bail_headstart + this_machine's_own_raw_bytes × 0.85 >
cap`. The 85% keep factor assumes as little as 85% of the forward
machine's own raw bytes survive minimization — a 15-point margin against
the ≤3.5-point shrink measured on the two witnesses in §2's table. This
follows the SAME "abort factor" methodology this codebase already uses
elsewhere (`compile.c`'s size-term ladder scratch bound, `3×` derived from
a measured 47.8% worst-case prose ratio) — a generous multiple of a
measured worst case, not an assumed one. **It is a margin, not a proof**,
and it is measured on exactly two witnesses. A wider sweep (post-lift,
over the full corpus and altwide set) is the real validation; if it finds
a forward-machine shrink ratio worse than ~15%, the margin needs
tightening. Flagged for ruling.

## 5. The numbers

All single compiles, `scripts/watchdog`-wrapped, this box. "Before" =
`main` at `56f34b01`, exported via `git archive` into scratch and built
there (no new worktree, per the scope mandate) — not a `pcrec-bench`
dependency.

### Refusal timing, altwide witnesses (read-only reference from pcrec-bench)

| pattern | before (wall) | after (wall) | reduction | before msg bytes | after msg bytes (projected) |
|---|---|---|---|---|---|
| `w-2048` | 10.97s | **1.55s** | 86% | 2,379,410 | 1,025,183 |
| `s-4096` | 19.58s | **12.51s** | 36% | 1,621,605 | 1,114,550 |
| `s-2048` | 5.25s | 5.27s | ~0% | 1,260,722 | 1,260,722 (identical — bail never proved it) |
| `sh1-512` | 0.13s | 0.13s | ~0% | 1,525,450 | 1,525,450 (identical) |

**The improvement is real but pattern-dependent, not uniform, and does
NOT reach the charter's "VM route's cost class" (~0.1s) target on every
witness.** `w-2048` gets close (1.55s). `s-4096` improves substantially
but not close to that target — its reverse machine is a smaller share of
its total (~26%, against `w-2048`'s ~36%), so the headstart buys less
runway. `s-2048` and `sh1-512` see NO improvement at all: their bail
threshold, under the current margin, is never crossed before raw
construction would have finished anyway (a SAFE outcome — same verdict,
same message, byte-for-byte on `s-2048` and `sh1-512` — just not a win).
This is the honest state of the feature, not a partial description of a
uniform one.

### Self-contained synthetic witness (no pcrec-bench dependency; the one the permanent check pins)

1,600 literal alternatives, 6-14 lowercase bytes each, `random.seed(1729)`:
before 12.15s (refuses at 2,929,087 bytes) → after **1.02s** (refuses at
1,256,802 bytes). This is the witness `tests/resource/
run_lim2_sizecap_projection.sh` uses.

### Verdict/reason parity, refused patterns

`w-2048`, `s-4096`, `s-2048`, `sh1-512` — before and after both refuse,
same stamped category either way. §5's table was measured before the
wording ruling (§6) landed, so its "after msg bytes" column shows the
OLD same-template wording with a smaller number; post-ruling, `w-2048`
and `s-4096` (where the bail fires early) now read `"projected at least
N bytes of emitted code"` instead, while `s-2048` and `sh1-512` (where
it does not fire) are BYTE-FOR-BYTE identical to "before", wording
included, since they fall through to the unchanged late check.

### Byte identity, accepted patterns

11 altwide patterns confirmed byte-for-byte identical between before and
after (same output basename in separate directories, to avoid a
self-referencing `#include` false mismatch that the first attempt hit and
is worth recording as a methodology note): `floor`, `w-8`, `sh1-64`,
`w-64`, `nar4-64`, `sfx-64`, `ci-256`, `srt-256`, `pfx3-256`, `nar4-256`,
`cnt-64`. This is a MANUAL, one-time sweep (not `make test`, not a
suite — the hold forbids both); the corpus-wide version is a `.lift` item.

## 6. The diagnostic wording — RULED (manager, 2026-09-04, lim2_rulings.md item 2)

The charter asked for "the SAME stamped reason and diagnostic the
post-emission check gives today"; the correction is that the byte figure
an early refusal has is partial, so the wording should say so rather than
imitate an exact one. **Ruled and implemented**: the two stamped fields
(`cx->size_cap_refused`/`_bytes`/`_limit`) and the refusal CATEGORY are
unchanged and identical either way (never `cx->dfa_overflowed` — that
field means "too many STATES", a different refusal). The TEXT now
differs by which check fires:

- post-emission (every route besides the DFA total cap, and the DFA
  route whenever the bail's margin does not prove the cap crossed
  early): unchanged, `"pattern too large: N bytes of emitted C source
  (limit L, ~K KB .o) ..."`, `N` the artifact's true final size.
- DFA route, early bail fires: `"pattern too large: projected at least
  N bytes of emitted code (limit L) ..."` — `N` the running total at
  the point of refusal, always less than the true final size would have
  been, `.o`-size estimate dropped (it is calibrated against a final
  total). Measured live: `pcrec: pattern too large: projected at least
  1256802 bytes of emitted code (limit 1000000). ...` on the §5
  synthetic witness.

`docs/spec/limits.md` §8 has the spec hunk; `tests/resource/
run_lim2_sizecap_projection.sh` asserts the EARLY wording specifically
(a witness that refused via the late wording instead would mean the
bail did not fire — the check's own signal for that regression, not a
pass).

## 7. Rulings received (manager, 2026-09-04, docs/dev/lanes/lim2_rulings.md)

1. **The `BAIL_KEEP_PCT = 85` margin is PROVISIONAL until a population
   proves it.** Ruled: the acceptance is a CENSUS built into the check
   script, post-lift (it needs the corpus) — per machine, over the whole
   corpus and the bench's altwide set, record raw table size vs. minimized
   table size, and ASSERT the margin exceeds the measured MAX forward
   shrink by at least 2×, RED with the distribution table otherwise. If
   the census ever finds a shrink the current margin does not clear, the
   margin moves to the census's number — never the reverse. Not yet
   built (needs `.lift`); §9 below is now sequenced around it.
2. **The diagnostic wording** — ruled and implemented, §6 above.
3. **`tests/resource` is the right home** — confirmed; no change needed.
4. **`size_bail`'s scope (forward table-engine build only)** — accepted
   per D77. The unmeasured machines (reverse, ENG_ATTEMPT/goto, the
   anchored machine) stay this row's named follow-on list, not built.
5. **`s-2048`/`sh1-512` (no benefit under the current margin)** — ruled
   OUT OF THIS STEP: filed as **[LIM-2] STEP 2 — an accept-table
   projection term**, with §5's numbers as its own starting measurement.
   Not built tonight; `docs/dev/plan.md`'s [LIM-2] row should gain a
   STEP 2 sub-line when that work actually begins (per this repo's own
   convention: expand into substeps only when work starts).

## 8. Delivery bar checklist

- [x] Branch builds clean under `make -j2` and `make strict`.
- [x] Projection refuses during construction with the same stamped
      category and message template (byte figure differs when the bail
      fires early — disclosed, §6).
- [~] Refusal-identity check: written (`tests/resource/
      run_lim2_sizecap_projection.sh`, self-contained, wired into `make
      test`), NOT run as a suite (hold). A manual, non-scripted single-
      compile sweep (§5) stands in for tonight.
- [x] Altwide cost table before/after (§5) — mixed results, honestly
      reported, not uniformly at target.
- [x] Byte identity on 11 accepted artifacts (§5), verdict/reason parity
      on 4 refused ones.
- [x] Spec hunk: `docs/spec/limits.md` §8 ("Handling an oversized
      artifact" 's lead-in), disclosing both the mechanism and the
      byte-figure-meaning deviation.
- [x] CLAUDE.md rows: `src/ir/CLAUDE.md`, `src/core/CLAUDE.md`,
      `src/gen/CLAUDE.md`, `tests/resource/CLAUDE.md`.
- [ ] `make test` / `make test-codegen` / `make test-registry` — post-lift
      items, per the brief's own phasing.

## 9. Post-`.lift` sequencing — what actually happened, in order

1. **`make -k -j4 PROCS=3 test`, first run** (background, log-polled):
   reached `tests/vm/run_vm_tests.sh` and found a REAL regression — §11.
2. **The census (ruling item 1) — built, run, RED** — §10. `PCREC_LIM2_
   BAIL_KEEP_PCT` (promoted from `src/ir/dfa.c`'s local `BAIL_KEEP_PCT`
   to `src/core/internal.h`, the `PREMUL_MAX_ENTRIES` precedent) is
   PROVISIONAL still: the census finds a real corpus pattern shrinking
   97.06%, and 2× that (194.1 points) exceeds what any percent-of-raw-
   bytes margin can express. NOT moved here — flagged for the manager,
   §10.
3. **§11's regression fixed** (`src/ir/dfa.c`'s size-bail refusal now
   also sets `cx->dfa_overflowed`, joining `intern()`'s two existing
   "pattern too complex" sites under the same umbrella `auto`'s [SEL-1]
   retry already reads) and verified standalone (`tests/vm/
   run_vm_tests.sh`: 52/52). One further, softer consequence of the SAME
   fix (this suite's OWN 1,600-literal witness becomes [SEL-1]-eligible
   too, and its flat alternation has nothing for the retry's count-
   collapse to shrink, so it fails a SECOND time against a different
   cap) is not a correctness regression (the pattern refuses both
   before and after) but broke this section's own diagnostic-identity
   check; fixed by building that witness under `--engine=dfa` (force),
   which isolates the mechanism under test from `auto`'s separate,
   correct, and orthogonal retry ladder. `tests/resource/
   run_lim2_sizecap_projection.sh`: 4/5 (the one RED is the census,
   §10, expected and reported, not a defect in this fix).
4. **`make -k -j4 PROCS=3 test`, second run** (clean rebuild, relaunched
   from scratch after killing the first run — it had kept running
   while `make -j4` rebuilt mid-flight, §11's own process-hygiene
   note): §12.
5. `make test-codegen`, `make test-registry`, `make test-axes`: §13.
6. Report final; DELIVERED — §14.

## 10. The census (ruling 1): built, run, RED for a real reason

`tests/resource/lim2_census.c` (own header: full methodology) links
`libpcrec.a` and drives the same internal pipeline `compile.c`'s D7 fast
path calls, under default options, to measure the forward table-engine
machine's REAL raw-vs-minimized byte shrink — not a re-derivation of the
bail's own decision (that would share a source with what it controls,
docs/dev/learnings.md §3); an independent re-run of real subset
construction and real minimization on real patterns.

**Population: 12** (`tests/**/*.rxt` corpus: 1; pcrec-bench's altwide
set, read-only: 11) — every pattern whose forward machine's RAW `n *
ncls` crosses `PREMUL_MAX_ENTRIES` (65,535), the regime the bail's
margin actually governs. Counted, non-empty, and both sources
contribute (a K35-shaped concern this report answers directly: the
corpus alone would not have exercised this population at all — see
below).

**MEASURED MAX forward shrink: 97.062%**, `tests/base/
k18_cost_gates.rxt`'s own compile-COST stress witness
(`(1{0,30}?[^]abc][^abc]){28,30}0+|a`, a deliberately expensive-to-BUILD,
small-once-built pattern): 27,575 raw states → 1,010 minimized (976,729
→ 28,693 bytes indexed-form). The two-witness manual estimate (§2, `<=
3.5%`) that `BAIL_KEEP_PCT=85` was calibrated against undercounts this
population's real worst case by more than 27×.

**RED.** Required margin per ruling 1 is `2 × 97.062 = 194.124` points;
`BAIL_KEEP_PCT=85` gives `100 - 85 = 15` points. `15 < 194.124`.

**NOT moved here, and the reason is itself a finding.** Ruling 1 says
"the margin moves to the census's number, never the reverse" — which
presumes a representable number exists. A `BAIL_KEEP_PCT` margin is
bounded at `[0, 100)` points; `194.124` points has no such value. This
is not a recalibration this lane can make unilaterally — it is evidence
that a PERCENT-OF-RAW-BYTES margin cannot, by construction, survive a
population that includes a pattern minimization shrinks by more than
50%, and `k18_cost_gates.rxt`'s witness is exactly that population,
legitimately in scope (it reaches the DFA route, crosses the threshold,
and its whole *point* — a cost-stress witness — is to be the kind of
pattern this mechanism has to survive). Left at 85, unchanged, pending
the manager's ruling. Three shapes were considered and not built,
named so they are not silently re-discovered: (a) exclude cost-gate-
style witnesses from the population — but nothing distinguishes them
from an ordinary corpus pattern except their OWN directory's stated
purpose, which is not a property `pcrec_build_dfa` can read; (b) widen
the margin's own SHAPE from a fixed percentage to something that can
express arbitrary shrink (e.g. an absolute floor beneath which the
projection defers to completion) — a real redesign, not a
recalibration; (c) scope the census's population further, to patterns
whose RAW bytes come within some proximity of the cap (since a pattern
nowhere near the cap can never trigger the bail regardless of shrink) —
narrows the *risk*, not the *promise* ruling 1 asked this census to
validate, and `k18_cost_gates.rxt`'s own raw bytes (976,729) are 97.7%
of the default cap, so it is not even a distant case under that
narrower reading either.

**No live false refusal exists TODAY at the default cap** — checked
directly: `--max-emit-bytes` is raise-only (cannot be lowered below the
default via the CLI to force the scenario), and at the shipped default
(1,000,000) `k18_cost_gates.rxt`'s own raw bytes (976,729) stay under
`bail_at` (~1,176,470 with this pattern's own headstart), so the early
bail does not fire for it. This is a NEAR MISS, not a demonstrated
regression, and a nearby variant (a slightly wider repeat count on the
same shape) could cross it while remaining just as tiny once minimized
— the general risk the census's own margin question is about.

**Representation-ambiguous after minimize: 5 of 12** — for these,
minimized `n * ncls` drops back to or below `PREMUL_MAX_ENTRIES`, so
`dfa_premul`'s own rule (which reads the MINIMIZED machine) could
legitimately choose the premultiplied form at emission, a DIFFERENT
representation than the indexed one both the census and the bail
assume. Argued NOT a correctness gap for the bail itself (docs header
of `lim2_census.c` and `tests/resource/lim2_census.c`'s own comment
carry the fuller argument): whenever the bail actually FIRES, raw
entries are — by construction of the check that guards the bail's own
action — still above the threshold, so construction aborts before
minimize ever runs and the ambiguous form is never actually reached on
that path. Recorded because it is a real, measured geometry fact about
this population, not because it changes what the bail promises.

## 11. A REAL regression, found by `make test` and fixed here

`tests/vm/run_vm_tests.sh`'s own `[SEL-1]` section carries a witness
pattern whose forward DFA has ALWAYS overflowed
`PCREC_MAX_DFA_STATES_TABLE` (>32,000 states) on this box. Before this
step, that overflow is diagnosed by `intern()`'s state-count check,
which sets `cx->dfa_overflowed` — the field `--engine=auto`'s [SEL-1]
retry ladder reads to fall back to the VM. The write phase's early
size-bail (this step's whole mechanism) now ALSO runs during the same
raw construction, and for this exact witness its projected byte total
crosses `PCREC_MAX_EMIT_BYTES` before the state count crosses 32,000 —
so the bail intercepts FIRST, and the write phase's delivered code set
only `cx->size_cap_refused`, deliberately NOT `dfa_overflowed` (that
code's own comment: "a different refusal this is not"). SEL-1's retry
eligibility reads ONLY `dfa_overflowed`, so it stopped firing for this
witness, and OPT-4's separate size-cap-retry rung does not apply either
(it explicitly excludes `fit.chosen == ENGM_DFA`, which this witness
is). Net effect: **a pattern that compiled today (`--engine=auto`
falling back to VM) started refusing outright** — precisely the
violation this step's own acceptance bar names ("the refusal set moves
NOT AT ALL"). `make test` found it; nothing in the write phase's own
11-pattern manual sweep or 4-pattern verdict-parity check could have
(neither exercises `--engine=auto` against a state-count-overflowing
witness).

**Fixed** (`src/ir/dfa.c`): the size-bail refusal now ALSO sets
`cx->dfa_overflowed` (with its own `dfa_overflow_why` text), reversing
the write phase's "deliberately not" call. The reversal is not a
special case: `intern()` ALREADY uses `dfa_overflowed` as an umbrella
for TWO distinct reasons (the state-count cap, K7's subset-elems cap),
both retry-eligible under `auto` regardless of `fit.chosen`, because
SEL-1 lets `auto` change its mind reactively whenever ANY in-progress
DFA construction does not pan out. A size overflow within the SAME
construction is a third instance of the identical claim, not a
different one.

**Verified**: `tests/vm/run_vm_tests.sh` standalone, 52/52 — the
witness falls back to VM again under `--engine=auto` (with an updated,
honest `RX_ENGINE_WHY` naming the projected-size reason rather than the
state count, since that IS what overflows first now), `--engine=dfa`
(force) still refuses do-or-die (wording updated to the early-bail
text), and `-fno-prefilter-collapse` is unchanged. `--engine=vm
-fprefilter` (force) STOPS refusing and starts compiling — traced to
`compile.c`'s OWN, pre-existing `size_eligible` rung ([OPT-4]/ruling B,
already unconditional on `--engine=auto`, already meant to honour
`-fprefilter`'s request with a collapsed prefilter rather than refuse
it), which could never reach this witness before (its `size_cap_refused`
was previously only ever set by the POST-EMISSION check, which the
state-count cap always pre-empted) — a pre-existing rung finally
reaching a population it was designed for, not a new mechanism. The
section's test file is updated to match, with the reasoning recorded
inline at each changed assertion.

**A second, non-correctness side effect of the SAME fix**: this suite's
OWN 1,600-literal witness (§5's "self-contained synthetic witness") is
now ALSO [SEL-1]-eligible under `--engine=auto`, and since its language
is a flat alternation with no repeated count, the retry's count-collapse
rung finds nothing to shrink — the retry rebuilds a VM prefilter that is
STILL too large, this time against `PCREC_MAX_VM_EMIT_CODE_BYTES`
(unrelated to this step), so the FINAL diagnostic under `auto` names a
different cap than the early bail's own. The pattern refuses either way
(no accept/refuse change), so this is not a correctness regression, but
`tests/resource/run_lim2_sizecap_projection.sh`'s own diagnostic-
identity check needed ONE diagnostic to assert — fixed by building that
witness under `--engine=dfa` (force), isolating the mechanism under
test from `auto`'s separate retry ladder.

**Process-hygiene note, recorded because it happened and the general
lesson is worth keeping**: the first `make test` background run was
still executing (well past `test-vm`, into `test-mrl`) when this fix's
own `make -j4` rebuild ran concurrently in the same worktree — a race
between a live test run and a rebuild of the binary it is testing. Found
via `ps` (never `pkill -f`, per this repo's own rule) and killed by exact
PID with `scripts/safekill`; the partially-rewritten `docs/dev/
artifact_size_log.tsv` from the interrupted run was reverted
(`git checkout --`) so the next full run regenerates it cleanly. `make
test` was relaunched from a clean, fully rebuilt tree with no further
concurrent source edits.

## 12. `make -k -j4 PROCS=3 test`, first full run (at `BAIL_KEEP_PCT=85`) — RESULTS

34/34 sections ran. **5 individual `FAIL:` lines, all found and fixed in
§11** (3 in `tests/prefilter/run_prefilter_tests.sh`, 2 in `tests/resource/
run_resource_tests.sh`) — no other section failed. Aggregate: 2,047 checks
passed across the run's own per-section summaries. `test-codegen` 109/0
(includes the K35 locale sweep, which found and counted this lane's own
4 new `sort` sites, all guarded); `test-registry` clean; the abi identity
gate reports `abi 20` unmoved on every artifact — see §14.

## 13. The margin move, applied for real, and re-validation

Per the manager's ruling (2026-09-04): `PCREC_LIM2_BAIL_KEEP_PCT` moved
from 85 to 1 (clamped; the required 194.124-point margin has no
representable value) in `src/core/internal.h`, on the real worktree,
rebuilt (`make -j4`, `make strict` clean). Two consequences already
covered in §11 as INVESTIGATED became the ACTUAL, real state of the
tree: `tests/vm/run_vm_tests.sh`'s `[SEL-1]` section is now
byte-identical in behaviour to pre-`[LIM-2]` main (confirmed: re-run
solo, 48/48, 3/3 scripts passed — no wording mismatch); `tests/resource/
run_resource_tests.sh` unaffected (still 30/30, the `a{65535}` reorder
finding is unrelated to the margin and stands as documented). The
census itself, re-run against the moved margin: population 12 unchanged,
margin now correctly reads 99pts (was 15), STILL RED — 99 does not clear
the 194.124pts the 97.062% shrink requires. `tests/resource/
run_lim2_sizecap_projection.sh`: 4/5, the 1 red being this same expected
census finding.

**The honest cost of the move, measured on a quiet box (load1
0.33-0.46), `--engine=dfa`, direct timing, w-2048 and s-4096 (the write
phase's own headline witnesses):**

| witness | main baseline | branch @ 85% (write phase) | branch @ census margin (=1) |
|---|---|---|---|
| w-2048 | 10.81s | 1.33s | **11.39s** |
| s-4096 | 19.32s | 12.62s | **19.24s** |

At the margin the census's own rule requires, the early bail does not
fire for either witness — both revert to the post-emission check,
byte-identical diagnostic wording to main — and the census-margin run is
NOT faster than main: w-2048 is 0.58s SLOWER (the reverse-first reorder
still runs, building and minimizing the reverse machine first, even when
it buys nothing); s-4096 is within noise. **The row's entire measured
win depended on the 85% margin the census disproved, and no margin
exists that both clears the census's 2x rule and keeps any part of that
win** — the arithmetic is unconditional: 2x of any shrink above 50%
exceeds the representable range. Reported to the manager 2026-09-04;
their call on whether the row ships, is scoped down, or is withdrawn
(census + diagnostics only, bail + reorder reverted) is pending as of
this report.

## 14. The abi question

**No.** This lane moves no emitted scaffolding — comment, declaration,
layout, or stamp — on any artifact. Argument: (a) the diagnostic-wording
changes (§6, §11) are compiler STDERR text at refusal time, never part
of an emitted artifact; (b) the reverse-then-forward build reorder is
argued order-independent for every emitted observable in its own
`compile.c` comment, and is now EMPIRICALLY confirmed by `make test`'s
own identity gates: every corpus/hybrid identity population in the full
run (`tests/codegen`, `tests/possessify`, `tests/rungselect`, `tests/
mrl`, etc.) reports 0 differing, and the abi stamp itself reads `abi 20`
unmoved (`[DD-14.FB]`'s own check: "rx_info carries the four sizing
fields with abi 20 on both engines"); (c) `PREMUL_DEAD`/
`PREMUL_MAX_ENTRIES`/`PCREC_LIM2_BAIL_KEEP_PCT`'s moves into
`src/core/internal.h`, and `pcrec_dfa_indexed_table_bytes`, are
compile-time-only source reorganisation with no emitted-text reader.
No abi bump owed at merge for this lane's own changes.
