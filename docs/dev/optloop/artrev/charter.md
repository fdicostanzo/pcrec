# [ARTREV] — bottom-up artifact review: charter

Frank, 2026-10-05 (ninety-second session): "generate a bunch of artifacts
then have the code be reviewed and look for optimizations, then a test and
timing compare of that one artifact. Expensive, but we can afford it this
week. Look for optimization leads bottom up. No SIMD. Deliverable is a
report of results with suggestions. Formalize the process. Independent of
the main workflow." Decision record: docs/dev/decisions.md D150.

## 1. What this is, and what it is not

Every optimization pcrec has shipped so far was found TOP-DOWN: a bench
cell loses, the cause is bucketed (D119), a mechanism is designed in the
emitter. ARTREV inverts the direction: read the C that pcrec actually
emits, the way a performance engineer reads any hot code, find what that
code does that it need not do, prove each idea on that ONE artifact by a
hand-edited twin (answer-identical, then timed), and only then ask which
emitter site produced it and how many artifacts share it.

It is a LEAD GENERATOR, not an optimization round. Its output is a report
and filed candidate rows under [OPTLOOP] (D137); nothing it finds is built
until a round selects it under D119/D144. It never edits `src/`, never
moves the abi, never touches main except its own docs and harness.

## 2. Restrictions (binding on every ARTREV lane)

- **No SIMD** (D119): no intrinsics, vector builtins, `vector_size`
  attributes, SWAR-over-wide-registers rewrites presented as scalar, or
  changed compile flags that enable vectorization. Scalar C only.
- **Compile flags are FIXED** at the bench's artifact flags (gcc, `-O2`;
  the selector records the exact line). A lead that only exists under other
  flags is recorded as such, never timed as a win.
- **The public ABI and stamps are preserved**: entry signatures, the
  `.abi`/selection stamps, capture semantics. A twin is a drop-in.
- **Pinned**: all artifacts are generated at ONE main sha (the first after
  START-SET stage 2 lands, abi 62), recorded with gcc version in every file.
  Twins are stored as PATCHES against the regenerated artifact, never as
  hand-maintained full copies (what moves on regeneration: everything; the
  patch either re-applies or the lead is re-checked).
- **Constants** a twin introduces (unroll widths, block sizes, cut-overs)
  are labelled measured / derived / unmeasured-default (D149).
- **Boxes**: the Mac carries generation, review, twins, identity and
  SCRATCH timing; ubuntubudu carries reportable timing, BY DAY ONLY (the
  bench owns the night). Bounds and locks: §3.1.
- **Scope mandate and BOILERPLATE** apply to every lane as usual; scratch
  under `build-artrev/` (gitignored) or the session scratchpad.

## 3. Roles and blindness

Frank, same evening: "give the artifact review lane the ability to test and
bench so it can iterate, but bound it." So the reviewer does not hand ideas
across a wall; it ITERATES (read -> twin -> verify -> time -> refine) with the
harness in its own hands, inside the bounds of §3.1. What the iterating lane
measures is WORKING data; what the report cites is an INDEPENDENT re-run
(S4) — the author never grades its own result (learnings §3).

| role | model | sees | does not see |
|---|---|---|---|
| harness builder | sonnet | everything | — |
| selector | sonnet | bench reports, gap report, D81 stamps, `pcrec` | — |
| reviewer-iterator | opus | ONE artifact (C + `gcc -O2 -S` asm), its pattern, its bench subject, `docs/spec/`, the `studies/artrev/` harness, the reviewer NOTEBOOK (§3.2) | `src/`, `docs/design/`, `plan.md`, decisions, known issues, other reviewers' full `review.md`s |
| confirmer | sonnet | the reviewer's final twins + harness | the reviewer's timing numbers until its own run is written |
| generalizer | opus | everything | — |

The reviewer is BLIND to the emitter on purpose (the D27 lesson: a reader
who knows why the code is shaped that way inherits its author's blind
spots). It works in a D27 cell (`scripts/mk_d27_cell.sh`) whose allowlist is
`docs/spec/`, `studies/artrev/` and its artifact directory; the brief carries
the usual disclosure requirement for spawn-time injections. Known-vs-new is
decided LATER by the generalizer, so blindness costs nothing but some
rediscovery, which is itself a signal.

### 3.1 The iteration bounds (enforced by the harness, not by good intent)

- **Leads**: at most 6 leads per artifact carried to a twin; at most 4
  twin REVISIONS per lead; at most 3 timing runs per revision.
- **Timing runs**: each one under `scripts/watchdog` (wall 10 min, RSS
  cap); the harness refuses to start one while `worktrees/.mac-suite.lock`
  exists or load1 is above its gate, and holds its own `build-artrev/
  .timing.lock` so two reviewers never time at once.
- **Boxes**: the Mac is where the lane iterates (SCRATCH tier — M1 numbers
  steer iteration and are never reported as results). ubuntubudu is
  available to the lane BY DAY ONLY (08:00-19:00 local, outside a declared
  bench window, `gnutimeout`, its own lock there too); the harness's remote
  wrapper refuses outside those hours.
- **Wall**: at most 6 hours per reviewer lane, then it finishes with what
  it has. Early stop: two consecutive leads ending NOISE or LOSS and no
  unread hot-path region left.
- **Every attempt is logged**: `iterations.tsv` gets one row per twin
  revision and per timing run, including the failures — a win chosen from
  many unlogged tries is a multiple-comparisons artefact, and the confirmer
  re-times only the final twins.
- **The SIMD and flag restrictions are checked mechanically**: the
  harness rejects a patch carrying intrinsics headers, `__builtin_ia32_*`
  / `__builtin_neon_*`, `vector_size`, or `#pragma GCC` optimize/target
  lines, and builds every arm with one fixed command line.

### 3.2 The reviewer notebook (Frank, 2026-10-05: memory between runs)

`docs/dev/optloop/artrev/notebook/` carries what earlier reviewers learned so
a later reviewer starts from it instead of from zero — a waste pattern found
in one artifact often recurs in the next.

- **One file per reviewer run** (`<artifact>-<reviewer>.md`), written at the
  end of the run and never edited by anyone else, so concurrent lanes never
  conflict. A reviewer READS every file present when it starts.
- **Entry shape**: the pattern of waste (how to SPOT it in emitted C/asm), the
  twin idea, the lane's scratch verdict, the identity pitfalls met, and
  ideas tried and abandoned with the reason. Written for a reader who has
  never seen this artifact.
- **The confirmer appends a `confirmed.md` row per lead** (WIN / LOSS / NOISE
  on Linux) so later reviewers know which ideas held up, not just which
  looked good on the Mac.
- **Blindness holds**: nothing from `src/`, the generalizer, `plan.md` or the
  design docs enters the notebook — it is reviewer-to-reviewer knowledge
  about ARTIFACTS only.
- **Provenance**: every lead in `leads.tsv` carries `origin` = `fresh` or
  `notebook:<entry>`, so the report can separate transfer from rediscovery
  (and measure what the notebook was worth).
- **The dual-review pilot artifact is the exception**: its two reviewers
  start with the notebook as it stood before either began and never see
  each other's entry until both finish — otherwise the overlap measurement
  measures the notebook, not independent review.

## 4. The process

**S0 — Harness + select.** The harness builder writes `studies/artrev/`:
generation at the pin, patch apply, the answer-identity driver and battery
generator, the timing driver (u3twin's shape: interleaved arms, rounds,
load gate, median + IQR), the bound enforcement of §3.1, and the remote
wrapper. Its own self-test includes the failing direction: a deliberately
wrong twin must FAIL identity, and a deliberately slowed twin must time as a
LOSS. The selector picks artifacts STRATIFIED by route (DFA scan / DFA
attempt / VM / hybrid / utf8; captures and no-caps) and by standing (losing
cell, near-tie, winning cell — winners are included because a winning
artifact can still waste work), every pick a cell the bench already times.
Output: `selection.tsv` + `artifacts/<name>/` (generated `.c`, `-S` asm, the
generation and compile lines).

**S1-S3 — Review and iterate** (reviewer-iterator, one artifact per lane).
Read the hot path first (the per-byte loop, the dispatch, the accept/commit
path), then setup and teardown. Every lead is a record in `leads.tsv`:
`id, artifact, site (function/label/line), observation, proposed change,
class, regime it should help, correctness argument, expected effect,
generality guess`. Classes: `redundant-work`, `control-flow`, `data-layout`,
`loop-structure`, `call-boundary`, `compiler-hint`, `algorithmic`, `other`.
For each lead: a twin as a patch (`twins/<lead-id>.patch`), answer identity
(the bench subjects, every corpus `.rxt` case for the pattern, the generated
battery: random over the pattern's alphabet, near-misses, lengths 0-64 and
around any block size the twin introduces, matches at subject start/end;
matches AND captures over every exported call shape; libpcre2 on a sample;
ASan + UBSan), then scratch timing, then refine within §3.1. ZERO identity
differences is the bar at every step, INCLUDING under shrunken resources:
identity also drives every caller-buffer entry (`_in`) with 0 and 1 frames
and trail and a reduced step budget, because a twin that drops frames or
trail can return a match where the original gives up (lane rvA09: its L4 r2
passed default-buffer identity with 284k such differences). THE GIVE-UP
RULE: where the ORIGINAL gives up (budget/frames/trail exhausted) and the
twin answers, the twin's answer must equal libpcre2's — a correct answer in
place of a give-up is the permitted repair direction (limits bound cost,
they are never part of the answer); a twin that gives up where the original
answers, or answers differently from the oracle, FAILS. A twin whose search
start can move earlier is also driven by a window-start differential
(rvA09's tool), never left to a livelock timeout. One NULL twin per artifact (a
semantics-free textual change) rides every timing run as the noise control.
The lane writes `review.md` (what the artifact does as read; each lead's
story including the revisions; what it checked and rejected and why).

**S4 — Confirm** (confirmer, ubuntubudu by day). A FRESH lane re-runs
identity and times the reviewer's final twins (original,
original-recompiled, null twin, each lead twin, a combined twin when two or
more leads survived) on the cell's subject plus one dense and one sparse
variant, ≥11 interleaved rounds. Plus a LAYOUT control: the original
and each winning twin re-built at >=4 code-offset pads (the method of
`docs/dev/optloop/k87twin_align.sh`), because a twin that changes code size
also moves alignment, and K87 measured layout alone at a few percent; the
harness's S0 null twin (an unused static function) measures recompile noise
only. A lead is a WIN only if its median beats the original by more than the
null twin's deviation, the arms' IQR AND the spread across pads, on the
cell's own subject; a LOSS by the same rule; otherwise NOISE. Only these
numbers enter the report. Optional: the top leads go to the bench as an
`[inbox]` I-note asking whether its rig can time an external-artifact arm (a
bench-only question, relayed — memory pcrec-ask-bench-dev).

**S5 — Generalize** (generalizer, not blind). For each surviving lead: the
emitter site(s) that produce the shape (`src/` file:line), the POPULATION
that shares it (a counted census over the corpus and bench exports at the
pin — K35: an uncounted population is not a finding), known-vs-new against
`plan.md` [OPTLOOP] candidates and `known_issues.md`, interaction with
in-flight work (START-SET stage 3 touches DFA seeding), the emitter-change
cost, and a suggested plan row (FILED, not scheduled — D137; Frank
ratifies).

**S6 — Report**. `docs/dev/optloop/artrev/report.md`: the selection and its
stratification; per artifact, the leads with their confirmed verdicts and
numbers, and the iteration history in brief; the null floor per cell; the
yield (leads per artifact, share surviving identity, share confirmed as
wins, and how often the lane's scratch verdict agreed with the confirmed
one); the ranked suggestions (measured gain x population / cost); what did
NOT work and why. An exec summary goes under `docs/dev/summaries/`.

## 5. Staging (measure the method before scaling it)

- **Pilot** — 3 artifacts (after the harness self-test is green): one DFA find-all on a LOSING cell, one VM with
  captures, one hybrid. On ONE of them, two independent blind reviewers
  (same brief, separate cells) — the overlap of their lead sets measures
  whether dual review is worth its cost in the full run.
- **Pilot gate** (manager): continue to the full run if at least one lead
  is a confirmed S4 WIN, or S5 finds a lead whose population is large even though its
  single-artifact effect sat in the noise; otherwise write the pilot report
  and stop. Recorded in the journal with the yield numbers.
- **Full run** — ~12-15 artifacts across the strata, single or dual review
  per the pilot's overlap measurement, S3-S6 as above.

## 6. Standing design-note questions (answered)

- **Measurement regime**: timing on ubuntubudu (Linux first-class), gcc
  -O2 as the bench compiles, interleaved rounds with load gate, the cell's
  own subject plus dense/sparse variants; Mac timing is never reported.
- **Independent control**: the null twin (shares the whole pipeline except
  the idea) for timing; libpcre2 for answers (independent of pcrec's code
  and of the reviewer).
- **What moves on regeneration**: every artifact; twins are patches against
  a recorded pin and re-apply or are re-checked; the generalizer maps each
  lead to an emitter site so the finding survives the artifact.

## 7. Where things live

- `docs/dev/optloop/artrev/` — this charter, `selection.tsv`, per-artifact
  `review.md` + `leads.tsv`, verdict tables, `report.md`.
- `studies/artrev/` — the harness (generation, patch apply, identity
  driver, battery generator, timing driver, summarizer), its own CLAUDE.md;
  never built by pcrec's make.
- Artifacts and builds — regenerated from the pin into `build-artrev/`
  (gitignored); only patches, tables and reports are committed.
