# [K59-PREMUL] — lane k59rung, 2026-09-17

Branch `lane/k59rung`, worktree `worktrees/k59rung`, built FROM `lane/dialimpl`
at `7bf9dade` (the parked dial branch — K59's own fixtures/pins live there and
invert in this same train, per the brief).

Executes Frank's K59 ruling (2026-09-17 morning): the drop ladder gains a
premultiplied-table rung, and the ladder becomes VERBOSE.
`docs/dev/known_issues.md` K59 is now marked **FIXED**.

---

## 1. THE RUNG

On an emitted-size cap refusal, `compile_driver`'s optional-contributor drop
ladder (`[K53-SELRETRY]`) may now ALSO deny `-fno-premul-table` for a
DFA-engine artifact's own retry — `SDR_NO_PREMUL` (`src/core/internal.h`),
`premul_eligible` (`src/core/compile.c`).

**ORDER: APPEND, as pre-ruled.** Rung 1 (`SDR_NO_ANCHORED`, the anchored
machine) stays first and undisturbed for its own population
(`drop_eligible`'s only change is tightening its budget conjunct from
`size_drop_rung < SDR_MAX` to `size_drop_rung == SDR_NONE` — SDR_MAX grew to
2 with the second rung, and the old spelling was only correct by the
coincidence that `anchored_ok` also goes false once rung 1 fires; made
explicit rather than left riding that coincidence). Rung 2 (`SDR_NO_PREMUL`)
is checked only when rung 1 declines — already fired and the artifact is
still over the cap, or never applicable (a caller's own explicit
`-fno-anchored-dfa`, the anchored machine's own STATE cap overflow, or a VM
hybrid). Both may fire on one artifact: `size_drop_rung`'s ordinal semantics
("every contributor up to and including this rung") compose them for free,
and `build_anchored_dfa`'s existing `>= SDR_NO_ANCHORED` gate already reads
correctly under `SDR_NO_PREMUL` with no change.

**THE MECHANISM IS SIMPLER THAN RUNG 1's, and that is a property of the
contributor rather than of effort spent.** Rung 1 needed a new gate at a
build site (`build_anchored_dfa` reading `Ctx.size_drop_rung`) because its
contributor is a MACHINE the driver decides whether to build. Rung 2's
contributor is a TABLE REPRESENTATION the emitter's own candidate list
already filters on `PCREC_NO_PREMUL_TABLE` (`src/gen/emit_dfa.c`'s
`dfa_premul`) — so the rung is spelled as the flag itself: `defo.flags |=
PCREC_NO_PREMUL_TABLE;` for every attempt from here on, exactly what
`[OPT-DIAL]`'s `--tune=-2` already does at driver entry. No new emitter
decision point; D82's single-decision-point rule is untouched.

**SCOPED TO THE DFA ENGINE** (`cx.job->fit.chosen == ENGM_DFA`), deliberately
narrower than the axis's full reach. `RX_DFA_TABLE` stamps on every artifact
with a DFA scan, including a VM hybrid's embedded prefilter table — but the
VM's own size-term (`[ART-SIZE]`) ladder is a multi-attempt state machine
(`st_phase`/`st_idx`/…) that, unlike rung 1's population, COULD have already
run by the time a VM-hybrid artifact reaches this catch block. Extending
rung 2 there would let a retry re-enter that ladder mid-ladder with no
measured need to justify the interaction (D77 — no VM-hybrid witness has
ever shown this necessary; K59's own filed repro is DFA-engine). Recorded as
a deliberate narrowing in three places (`SDR_NO_PREMUL`'s own comment,
`compile.c`'s premul_eligible block, `docs/spec/limits.md`), not silently
assumed.

**THE FORCE-FLAG EXCLUSION THE BRIEF ASKED FOR IS VACUOUS, NOT UNBUILT — A
FINDING AGAINST THE BRIEF'S OWN PREMISE.** I checked `cli/main.c` and
`lib/pcrec.h` before writing the eligibility test: `-fno-premul-table` is
DENY-ONLY (`tuning.md` §2.13's own text: "there is one table form per
machine and the compiler picks it, so there is nothing to address and
nothing to force"). No `-fpremul-table` spelling exists anywhere in the
tree. So "an explicit force excludes the rung" has no code to write; what
DOES need to be handled — an explicit `-fno-premul-table` from the caller —
is handled for free by the eligibility test's own conjunct
(`!(defo.flags & PCREC_NO_PREMUL_TABLE)`): the flag is already set, the
rung's own OR adds nothing, and the rung correctly declines rather than
re-firing. If a force spelling is ever added, `premul_eligible` needs the
identical conjunct `-fprefilter` carries against `[OPT-4]`'s own rung
(explicit beats rescue) — stated as an obligation at three sites rather than
silently omitted.

**MEASURED, K59's own filed repro** (`[^\p{C}\p{M}\p{P}]` under `-e utf8
--features unicode-props`), all five `--tune` positions, this branch's tip:

| position | before this lane | after | rungs fired |
|---|---:|---:|---|
| `balanced` (0) | REFUSED (1,027,199 B) | **453,525 B** | both |
| `size` (-1) | REFUSED (1,027,196 B) | **453,521 B** | both |
| `min-size` (-2) | compiled, 608,196 B | 608,196 B (unchanged) | neither — the CALLER's own flag alone is sufficient |
| `speed` (+1) | REFUSED (1,027,198 B) | **453,522 B** | both |
| `max-speed` (+2) | REFUSED (1,027,206 B) | **453,526 B** | both |

**The refusal set is identical again, BY MECHANISM.** All five positions now
compile the SAME language — the drop ladder's two rungs are both
answer-preserving form axes (the K53-SELRETRY precedent's own membership
rule: answer-preserving, observable in the artifact's own stamps, smaller),
never language ones. `tests/size/tune_dial_fixtures.rxtin`'s F3 asserts this
directly (a live `m`/`n` block replacing the `perr`, all five positions
agreeing on "A" matching and "!"/""/"\x01" not), not merely via byte counts.

**Stamp distinguishability — VERIFIED, not claimed** (item 4 of the brief).
Live at this commit:

- `--tune=balanced`: `RX_ENGINE_SEL "size-cap-retry"`, `RX_DFA_MATCH
  "search-filter"` (rung 1), `RX_DFA_TABLE "indexed"` (rung 2) — both fired.
- `--tune=min-size`: `RX_ENGINE_SEL "selected"`, `RX_DFA_MATCH "unwrapped"`
  (the anchored machine SURVIVES), `RX_DFA_TABLE "indexed"` (the caller's
  own explicit denial, not this ladder) — the K53 report's own §3.1a control
  shape, reproduced live.

`tests/codegen/run_tune_dial.sh` §6 asserts this combination at all five
positions as a permanent check, not a one-off transcript.

---

## 2. THE VERBOSE NOTE (Frank's addendum, general mechanism)

Every rung firing — the pre-existing anchored rung too, which shipped with
the OPPOSITE ruling ("no stderr note", K53's own report §2, citing [LIM-2]
N1's precedent for when one is warranted) — now prints a loud, non-fatal
stderr note. ONE shared helper, `size_drop_note()` (`src/core/compile.c`,
placed immediately before `compile_driver`), called once per rung that
ACTUALLY FIRED on this compile (`dropped_anchored`/`dropped_premul`, tracked
separately from `size_drop_rung`'s ordinal — see below for why the ordinal
alone cannot tell "fired" from "never applicable"), at the WARN_EMIT_BYTES
note's own placement rule (past the recovery point, on the attempt about to
succeed, never on a discarded trial).

**Live wording** (both rungs firing, `--tune=balanced`):

```
pcrec: note: the emitted-size cap forced a smaller artifact: dropped the
optional anchored match-here machine -- loses the [OPT-2] fast path --
<prefix>_match falls back to search-and-filter, which the anchored machine
exists specifically to avoid (docs/design/anchored_match_unwrapped.md).
Raise --max-emit-bytes/--max-emit-code-bytes to keep the faster form, or
accept the fit.
pcrec: note: the emitted-size cap forced a smaller artifact: dropped the
premultiplied DFA transition table -- slower per-byte scan dispatch,
measured ~1.27x on scan-bound subjects
(docs/dev/opt3_dfa_scan_measurement.md). Raise --max-emit-bytes/
--max-emit-code-bytes to keep the faster form, or accept the fit.
```

The ~1.27x figure is cited from `docs/dev/opt3_dfa_scan_measurement.md`
rather than invented, per the brief's own instruction. Two lines each,
naming what/cost-direction/recourse. `--tune=min-size` prints NEITHER note
(neither rung fires there — verified: the check fails loudly if a note
prints where no rung ran, guarding the opposite direction the brief did not
explicitly ask for but that seemed worth closing given the shared-source
discipline).

**Why two tracking bools rather than reading `size_drop_rung`'s ordinal
directly.** Rung 2 can reach `SDR_NO_PREMUL` (2) WITHOUT rung 1 ever having
fired, whenever rung 1 was inapplicable — `size_drop_rung`'s own
"everything up to and including" semantics then makes `size_drop_rung >=
SDR_NO_ANCHORED` read true even though the anchored machine was never
dropped by THIS retry (it may never have existed, or been denied by the
caller for an unrelated reason predating this compile). Reading the ordinal
for the note's wording would misattribute a caller's own pre-existing
`-fno-anchored-dfa` as "this rung dropped it". `dropped_anchored`/
`dropped_premul` are set only at the exact point each rung's own eligibility
block fires, so the note names only what THIS retry actually did.

Scoped strictly to the `Ctx.size_drop_rung` ladder (K53 + K59); `[OPT-4]`'s
separate VM-hybrid prefilter-collapse rung is NOT touched — the brief's own
language ("the ladder... every rung") reads as the two-rung `size_drop_rung`
ladder specifically, and OPT-4's rung has its own established (and
apparently deliberate) silence. Flagged as a reading, open to correction.

---

## 3. K59 CLOSES

`docs/dev/known_issues.md` K59 gains the FIXED marker (disposition 2,
mechanism, date), with the ORIGINAL filed text preserved verbatim beneath it
per the house convention (K28/K7/K27/etc.'s own precedent).

**Inverted pins/fixtures** (all in `lane/dialimpl`'s own delivered material,
now on this branch):

| file | before | after |
|---|---|---|
| `tests/size/tune_dial_fixtures.rxtin` F3 | `perr` block, header records the violation | live `pattern`/`m`/`n` block, all 5 positions match "A" / refuse "!"/""/"\x01" identically; header records the fix |
| `tests/codegen/run_tune_dial.sh` §6 | asserts compiles-at-`-2`-alone / refuses-at-other-four as MEASURED CURRENT BEHAVIOUR | asserts compiles-at-all-five, stamps distinguish which rung(s) fired, verbose note fires exactly there — 17/17 checks pass (was 17/17 asserting the violation) |
| `tests/size/CLAUDE.md` | F3 described as the filed violation | F3 described as the fix, mechanism named |
| `docs/dev/known_issues.md` | K59 open | K59 FIXED, original preserved |
| `docs/spec/limits.md` | one-rung ladder | two-rung ladder, verbose note documented |
| `docs/spec/tuning.md` §2.13/§2.15 | no cross-reference between the two rungs | each references the other, K59's resolution stated |
| `src/core/CLAUDE.md` | K59 recorded as open (tune.c section), one-contributor rung (compile.c section) | both updated: K59 FIXED, second contributor documented |

Design doc `docs/design/opt_dial_design.md` carries NO K59 mention (K59 was
found by `dialimpl` after that note was written, during implementation) —
checked, nothing to annotate there.

`tune.c`'s policy table is UNCHANGED. The `-2` cell's `-fno-premul-table`
denial is exactly as ratified; disposition 1 (narrow the cell) was NOT
taken, per Frank's ruling.

---

## 4. STAMPS

The retry event reuses `ESEL_SIZE_CAP_RETRY` — [LIM-1]'s value, unchanged —
per the precedent both K53's own report and the brief cite. No new stamp
value, no `abi` bump: NO emitted byte moves for any artifact that already
compiled before this change (the rung only ever fires on an artifact that
was PREVIOUSLY REFUSED; verified by the corpus-wide reasoning K53's own
report uses for the identical claim — the rung is reached only from a
refusal, so it cannot move an artifact that already existed. A full corpus
byte-identity sweep like K53's own §3.2 was NOT re-run here — OWED, see §6 —
but the argument is structural rather than merely likely: `premul_eligible`
requires `cx.size_cap_refused`, which by construction never holds on a
previously-accepted attempt).

`ESEL_SIZE_CAP_RETRY`'s own comment (`src/core/internal.h`) is updated from
a two-row "mutually exclusive by engine" table to a three-row one, stating
explicitly that rungs 1 and 2 of the drop ladder are NOT mutually exclusive
with each other (both DFA-engine) the way either is with `[OPT-4]`'s
VM-hybrid rung.

---

## 5. TESTS

- `tests/codegen/run_tune_dial.sh` §6 — rewritten (§1 of this report). Live
  run: **17/17 pass** (all sections, not just §6).
- `tests/size/tune_dial_fixtures.rxtin` — F3 rewritten. Live run via
  `tests/harness/run.sh tests/size/tune_dial_fixtures.rxtin`: **10/10
  cases pass, 0 failed, 0 pattern-compile failures** (F1/F2/F3 combined).
- `tests/codegen/run_anchored_match.sh` (K53's own suite — unaffected by
  this rung by construction, re-run to confirm no regression from the
  `drop_eligible` tightening): **20/20 pass**, population figures unchanged
  from K53's own landing (`search-filter(size-drop) 11`).
- `tests/codegen/run_premul_table.sh` ([OPT-3]'s own suite, unaffected by
  construction, re-run to confirm): **16/16 pass**.
- `tests/rxtsource/run_rxtsource_tests.sh`: **212/212 checks + 1 recorded**,
  census **210 files / 3936 blocks / 28943 expectation lines — unchanged**
  from the branch point (the `.rxtin` fixture is deliberately outside the
  census by convention, per its own directory's CLAUDE.md).
- `make strict`: clean at every commit in this lane.
- Two new mech sabotage rows, `S252`/`S253` (highest id on this worktree
  before them was `S251`), both **field-validated** (`VALIDATE_ONLY=1`) and
  both run through the **real mech driver** (`bash
  tests/mech/run_sabotage_matrix.sh S252`/`S253`):
  - **S252** — the rung's eligibility test defeated (S237's shape, one rung
    over). `reach:ok(1/1), tunedial:4fail/16pass` — **DETECTED**.
  - **S253** — the rung fires but `dropped_premul` is never set, so the
    verbose note never prints even though the artifact and its stamps are
    unaffected (S238's shape, one rung over — a silent rescue where the
    ladder's own new contract demands a loud one). `reach:ok(1/1),
    tunedial:4fail/16pass` — **DETECTED**.
  - Re-anchoring **S237** was required (tightening `drop_eligible`'s budget
    conjunct moved its anchor text) — re-derived from `git show HEAD:`,
    intent re-verified by construction (the substitution still reads
    `false;`, `drop_eligible` still governs only the anchored-machine drop),
    and re-run through the real driver: `reach:ok(1/1),
    anchoredmatch:4fail/19pass` — **DETECTED**, matching its pre-fix shape
    (K53's own report cites `anchoredmatch` red on 4 checks under the
    identical plant).
  - `python3 scripts/m6read_check_sab_anchors.py`: **all anchors resolve**
    (261 sabotages / 277 anchor sites) after the S237 re-anchor.

---

## 6. WHAT IS OWED

- **The full battery** (`make test`, `mech`, `san`, `axes`, `lint`) — the
  manager's at merge, per standing policy. Not run here.
- **A full corpus byte-identity sweep** confirming no previously-accepted
  artifact moved a byte (K53's own §3.2 shape). Argued structurally above
  (the rung's eligibility requires a size-cap refusal, which cannot hold on
  an artifact that already compiled) but not independently measured over
  the whole corpus.
- **`tests/axes/run_axes.sh`'s DIAL-S3 arm at the new tip** — confirms 0
  gained / 0 lost on the shipped corpus population at every `--tune`
  position (K59's own witness is a constructed fixture; the shipped corpus
  should be unaffected by construction, same reasoning as above, unverified
  by a fresh run here).

**NOT OWED, named so nobody goes looking**: a third drop-ladder rung for a
`+2`-induced `VM_INLINE_CHAIN_MAX_BYTES` overflow (`docs/spec/limits.md`'s
own "still no rung" gap, unrelated to K59, D77 — no witness exists);
extending rung 2 to the VM engine (D77, scoped deliberately, §1 above).

---

## 7. FILES CHANGED

**Compiler.** `src/core/internal.h` (`SDR_NO_PREMUL`, `SDR_MAX` 1→2,
`ESEL_SIZE_CAP_RETRY`'s comment). `src/core/compile.c` (`premul_eligible`
block, `drop_eligible`'s tightened conjunct, `dropped_anchored`/
`dropped_premul`, `size_drop_note()` + its two call sites,
`COMPILE_MAX_ATTEMPTS`/exhaustion-message comments).

**Spec (D80).** `docs/spec/limits.md` ("The optional-contributor drop"
section rewritten for two rungs + the verbose note), `docs/spec/tuning.md`
(§2.13, §2.15 cross-referenced).

**Docs.** `docs/dev/known_issues.md` (K59 FIXED), `src/core/CLAUDE.md` (two
sections updated), `tests/size/CLAUDE.md` (F3's description rewritten).

**Tests.** `tests/codegen/run_tune_dial.sh` (§6 rewritten),
`tests/size/tune_dial_fixtures.rxtin` (F3 rewritten),
`tests/mech/sabotages/S252_premul_drop_rung_deleted.sh` (new),
`tests/mech/sabotages/S253_premul_drop_note_unstamped.sh` (new),
`tests/mech/sabotages/S237_size_drop_rung_deleted.sh` (re-anchored).

No `abi` bump (§4). No files under `src/opt/select_engine.c` touched — its
`ESEL_SIZE_CAP_RETRY` arm already read `size_drop_rung != SDR_NONE`
generically and needed no change for the new ordinal value.
