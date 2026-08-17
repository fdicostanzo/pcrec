# tests/mech — GENERATE the sabotage detection tables ([MECH-1])

Every "disabling X fails N cases" figure that used to live by hand in
`tests/*/CLAUDE.md` goes stale silently, and every attempt to maintain one by
hand in this project has failed at least once — including twice inside the
same review, and once inside the paragraph written specifically to warn about
it (see `tests/reject/CLAUDE.md`). This directory owns the sabotage EDITS
themselves, applies each to a pristine tree, and prints a matrix instead of a
copied number. Docs should cite this script's output, not a hand-typed count.

## Files

- **run_sabotage_matrix.sh** — the driver. For each sabotage: build a FRESH
  tree from `git archive HEAD` (never a copy of the real working tree, never a
  reused/reverted tree — the [MECH-2] lesson), apply the edit through
  `lib/replace.py`, build it (`make all` inside the scratch tree only — this
  never runs `make` in the real repository), run the suites the sabotage's own
  table says are relevant, and print one row of the matrix. Supports running a
  single sabotage by id prefix: `bash tests/mech/run_sabotage_matrix.sh S13`.
  Env: `CC`, `KEEP=1` (keep scratch trees + suite logs instead of deleting
  them), `MECH_SCRATCH` (scratch root), `JOBS`, and `PROCS=N` (2026-08-12) —
  N sabotages concurrently, safe because run_one was already isolated per
  sabotage; rows are merged in sabotages/ listing order so the matrix is
  byte-identical to a serial run's, and `JOBS` defaults to nproc/PROCS so
  concurrent tree builds do not oversubscribe. In BOTH modes the summary now
  guards its row count against the number of definitions requested: before
  this, a sabotage whose definition failed validation produced NO row and the
  denominator (`wc -l` of arrived rows) silently shrank — 19/19 reads as
  clean where 20 were asked for. That is the checks-sharing-a-source shape
  again, fixed by counting the demand side from the `sabotages/S*.sh` listing.
  Validated in the failing direction with a stub definition missing
  `SAB_FILE`: FATAL exit 2, the missing sabotage named.
  A successful run ends with a grep-able COMPLETION TRAILER
  (`== mech run COMPLETE: <N> rows (undetected: U, anomalies: A) at <SHA> ==`),
  added 2026-08-12 (fourteenth session) after a finished run was twice
  reported still-running: **never poll a run's liveness with
  `pgrep -f "make mech"`** (or any pattern naming this script) — the session
  harness wraps every polling command in a shell whose own command line
  contains the pattern, so the poll matches itself and answers RUNNING
  forever. Completion is a fact about the log: grep it for the trailer, or
  for FATAL (the only early exit that skips it). The run also now removes
  its mktemp'd scratch root and parallel-mode row dir on exit (KEEP=1
  preserves both; a scratch root passed in via MECH_SCRATCH is never
  removed).
- **lib/replace.py** — the ONLY thing that edits a sabotaged file. Takes a
  target file plus literal BEFORE/AFTER text and a required occurrence count;
  refuses to run if the anchor text is not found exactly that many times
  (source drifted since the sabotage was written — this is the anchor-mismatch
  failure mode this tool exists to make loud instead of silent), refuses if
  BEFORE == AFTER (a no-op sabotage is a bug in the definition), and refuses to
  trust the result unless the AFTER text is actually present afterward. One
  mechanism for every sabotage, whether it is a substitution, an insertion
  (BEFORE is a prefix of AFTER), or a deletion (AFTER is empty).
- **sabotages/S\*.sh** — one file per sabotage, sourced by the driver. Sets
  `SAB_ID`, `SAB_FILE`, `SAB_SUITES` (space-separated: `codegen` `trie`
  `reject` `harness` `registry` `pc3` `cli` `vmidentity` `vm`), `SAB_DESC`,
  `SAB_BEFORE`, `SAB_AFTER`, and optionally
  `SAB_COUNT` (default 1) and `SAB_HARNESS_TARGET` (an .rxt file or dir to
  scope the `harness` suite to, instead of the whole corpus). Each file also
  carries `SAB_DOC_FIGURE`, a comment-and-string record of what the source
  documentation claimed, purely for humans diffing a re-run against the docs —
  the matrix itself does not read it.

## What "suites" means here

- `codegen` → `tests/codegen/run_codegen_tests.sh` (OS-0b/OS-1/TS-1/skip
  checks, ~28 structural checks bundled in one script).
- `trie` → `tests/codegen/run_trie_identity.sh` (the M2.8 differential check,
  default 500 patterns x 2 sweeps, plus 3 positive controls).
- `reject` → `tests/reject/run_reject_tests.sh` (the "requires module 'X'"
  mandate, hand-written + iterated + accept-control rows).
- `harness` → `tests/harness/run.sh`, optionally scoped to
  `SAB_HARNESS_TARGET` for speed (most sabotages here only need
  `tests/base/caseless.rxt`, not the full corpus).
- `registry` → `tests/registry/registry_check.c` (built against the sabotaged
  tree's own `libpcrec.a`) plus the two `compliance_section.py` checks. This is
  tests/registry/ MINUS its libpcre2 half — the pcrec-reading-pcrec net.
- `pc3` → `tests/registry/pcre2_check.c`, the EXTERNAL check. Needs libpcre2 at
  run time and **skips loudly per row** when it is absent (see below).
- `cli` → `tests/cli/run_cli_tests.sh`. Note the scrape: this script counts
  `cases`, like the corpus harness, not `checks` like every other arm.
- `vmidentity` → `tests/codegen/run_vm_identity.sh`, the [M4.5b]
  zero-regression gate. A SEPARATE arm from `codegen` even though the script
  lives in that directory: what it guards (a capture-free pattern's emitted
  bytes do not move) is orthogonal to every optimization-present check in
  `run_codegen_tests.sh`, and a sabotage of one should not be reported as
  coverage by the other.
- `gentimeout` → `tests/lib/run_gen_timeout_tests.sh`, D45's own checks. Its
  own arm because what it guards is a property of the TEST INFRASTRUCTURE,
  which no other arm can see: with the budget removed every suite still
  passes and only the next multi-hour hang notices.
- `irlisting` → `tests/codegen/run_ir_listing.sh`, [M4.5c]'s DD-8 listing
  check. Its own arm rather than `codegen` or `vmidentity`, for the reason
  those two are separate from each other: what it guards (the program listing
  cannot drift from the artifact it describes) is orthogonal to both, and a
  sabotage of one must not be reported as coverage by another.
- `vm` → `tests/vm/run_vm_tests.sh`, the [M4.5b] VM engine section (the two
  bounds, the artifact stamps, and the capture oracle + §3.7 differential
  sweep). The sweep dominates its runtime, which is why this arm is assigned
  only where a sabotage's signal is a WRONG SPAN or a broken bound — never
  "just in case".

The last three landed 2026-08-12 (MOD-0.8c slice 1), and **neither arm runs
`run_registry_tests.sh` itself** even though that is what `make test` runs.
Two reasons, both about what a matrix cell is allowed to mean. The wrapper
fuses the internal and external checks into one exit code, and which of the two
sees a sabotage is usually the whole finding — S16 is interesting precisely
because `registry` and `pc3` both score zero on it. And the wrapper's coverage
guards fire on a changed PASS COUNT, so a check that legitimately failed would
also trip "coverage changed", and the cell could not distinguish detection from
a count moving.

**The cost was measured before the arms were wired, not asserted after**
(docs/dev/plan_completed.md's [MOD-0.8c] row requires that order). One scratch archive tree
at `11352be` on a 12-core box: `git archive HEAD` 0.04s, `make all -j12` 0.75s,
then build-and-run per suite — `registry` 0.60s, `pc3` 4.36s, `cli` 5.46s,
against the `reject` arm's **54.75s** that S15-S20 were already paying. All
three together cost about a fifth of the one arm those rows already ran, which
is why the retagging below was not a cost question.

## `pc3` can SKIP, and a skip is not a pass

`pcre2_check.c` dlopens libpcre2 and exits 0 with `SKIP:` lines when it is
absent — the convention that keeps a stranger's clone green. The arm reproduces
that as a **visible `pc3:SKIPPED-no-oracle` cell**, never as a silent zero, and
the verdict logic refuses to let it read as evidence:

- a row whose assigned suites ALL skipped is `INCONCLUSIVE`, never
  `UNDETECTED` — the latter is a finding, and it would be a false one;
- a row that ran something else carries `(pc3 SKIPPED -- no oracle)` appended
  to its verdict, because "caught by nothing" means something different when
  one of the nets was not in the water;
- the end-of-run summary lists every skipped row, and the completion trailer
  counts them: `== mech run COMPLETE: N rows (undetected: U, anomalies: A,
  pc3-skipped: S) at <SHA> ==`.

That last field is new in the trailer; the grep-able prefix is unchanged.

**Both skip branches are validated in the failing direction** (2026-08-12) — a
branch that exists for a rare environment and has never run is the dead-branch-
reading-as-coverage shape this directory keeps finding. Measured in a throwaway
scratch repo whose `tests/fuzz/pcre2_abi.h` SONAME list points at a nonexistent
library, which is the documented way to make PC-3 skip:

    pc3 the ONLY arm   pc3:SKIPPED-no-oracle
                       INCONCLUSIVE -- every assigned suite SKIPPED (no libpcre2 oracle)
    S19 (reject+registry+pc3)
                       reject:1fail/486pass,registry:1fail/169pass+compliance-FAIL,pc3:SKIPPED-no-oracle
                       DETECTED (pc3 SKIPPED -- no oracle)

Neither said UNDETECTED, which is the property that matters: with the oracle
missing, "caught by nothing" is not a finding, and the summary block and the
trailer's `pc3-skipped` count both fired.

`make bench` and PC-4 (`run_pc4.sh`, measured 2.50s) are the two suites still
deliberately NOT wired, for the same reason: no sabotage's ONLY signal is a
throughput budget or a semantic differential today. Add the arm in the same
change as the first sabotage that needs it.

## [M4.5b]'s five rows (2026-08-15)

S36-S40 cover the VM emitter, and two of them are not invented failures:
**S38** (an empty iteration rolled back instead of taking the loop's exit
continuation) and **S39** (the span-loop cursor emitting its greedy shape for
lazy quantifiers) are the two bugs that emitter actually shipped in its first
draft. `tests/vm/vm_oracle.py` found both against python `re`; the sabotages
restore them verbatim so the sweep is required to keep finding them. A
sabotage whose edit is a real past bug is worth more than an invented one —
it proves the check catches what the code is actually prone to, not what the
check's author imagined.

Run them as `bash tests/mech/run_sabotage_matrix.sh S36` (and S37..S40), and
read the numbers from that output, never from prose anywhere.

## [M4.5c]'s two rows (2026-08-15)

S41 and S42 both attack engine_m4.md §10's one constraint on DD-8's dump —
that it derive from the same structure the emitter walks — from the two
directions it can fail: a label emitted without being recorded (S41) and a
choice point recorded nowhere while the artifact still pushes it (S42). In
both the ARTIFACT is unchanged and only the dump lies, so no correctness test
anywhere in the tree can see either.

S41 is the third sabotage in this directory whose edit is a real past bug
rather than an invented one: the accept label really was emitted by a direct
`sb_printf`, and `run_ir_listing.sh` caught it on its first run.

## [M4.5c fix]'s two rows (2026-08-15, D45)

S43 removes D45's compile budget and S44 raises the replication cap out of the
way. Both restore a state the tree really shipped in: S43's is how every
compile looked before the ruling (which is why a 100-minute hang went
unnoticed), and S44's is what let `((a)|b){0,4000}c` emit 3.5 MB (K19).

They also demonstrate that the two guards are INDEPENDENT, which is worth
having in the matrix: the compiler-side cap stops the artifact existing, the
harness-side budget stops any artifact hanging a battery, and neither
subsumes the other.

## Which rows were retagged, and what the new arms measured

Six rows gained arms at MOD-0.8c slice 1 — the ones whose own documentation
names these suites as their relevant net. Both runs are at `11352be`; `before`
is the same matrix with `reject` as the only arm. Every row was DETECTED in
both runs, so the deltas are in the CELLS, which is where the information is.

| row | before | what the new arms added |
|---|---|---|
| S15 drop `\d` row | reject 12 | registry **2** (+compliance), pc3 **0** — PC-3 iterates rows that EXIST, so a deleted one is invisible to it; the exact row count is what sees this |
| S16 wrong module | reject 5 | registry_check **0**, pc3 **0** — both prose claims confirmed as measured zeros (see the row's own header for the `+compliance-FAIL` caveat) |
| S17 syntax probe | reject 1 | registry **3**, pc3 **1** — both fire, for different reasons: the probe stops reaching pcrec's doorway, and stops being a construct libpcre2 can be asked about |
| S18 empty TSV | reject 1 | registry **0**+compliance-FAIL, cli **8** — the `cli` arm's first user; case10 counts the dump's fields |
| S19 fabricated row | reject 1 | registry **1**, pc3 **1** — the documented blind spot, closed; see the section above |
| S20 `\d` as literal | reject 9 | registry **4**, pc3 **1** — the `\v`-bug shape, now with an external answer |

The `+compliance-FAIL` on five of the six is `compliance_section.py --check`
noticing that docs/pcre2_compliance.md's generated index no longer matches the
table. Read it as visibility, not as a control: its own failure message names
`--write` as the remedy, which regenerates the doc from the sabotaged table and
goes green.

`make bench` is deliberately NOT wired in here — R3.1 already measured that
S01's skip-state sabotage also fails bench case (e)'s throughput budget, but
running bench per-sabotage would make a ~10-sabotage sweep minutes slower for
a signal the codegen suite's structural check already gives for free. Add a
`bench` suite case here if a future sabotage's ONLY signal is a throughput
budget.

## A sabotage that zero checks catch is the finding, not a bug

If every suite a sabotage lists comes back with 0 failures, the matrix marks
that row `**UNDETECTED**` and calls it out again in a summary block at the
end. An UNDETECTED verdict means a guard regressed and is the thing to go fix.

**As of 2026-08-12 there are no UNDETECTED rows** (35 of 35 DETECTED, 0
anomalies, 0 pc3-skipped), and the row that used to be the standing exception
is worth reading before anyone re-adds one.

`S19-new-wrong-row` — the SR-4 blind spot, "a NEW row with a plausible wrong
module and no hand-written entry" — was documented HERE and in its own header
as EXPECTED to land UNDETECTED, with PC-3 named as the only thing that could
see it and declared out of scope for this matrix. Both halves of that were
retired at MOD-0.8c slice 1, and the two failure modes are different lessons:

- **It had already stopped being UNDETECTED, and nothing noticed.** Measured
  at `11352be` with `reject` as its only arm, BEFORE the new arms existed:
  `reject 1fail/486pass`. The exact iterated-row count (100 ≠ 101) trips, as
  `tests/reject/CLAUDE.md` records. A hand-maintained "expected UNDETECTED"
  that had quietly become DETECTED is precisely the staleness this directory
  exists to prevent — occurring in the directory that exists to prevent it,
  which is this project's oldest recurring shape and its fourth instance.
- **PC-3 is in scope now**, because there is a `pc3` arm. Measured:
  `pc3 1fail/154pass` — libpcre2 has no `\j`, so the fabricated `RS_MODULE`
  row fails PC-3's "a row naming a construct PCRE2 does not have" clause.
  That is an external answer rather than a count moving, which matters: R8/C4-10
  records that a count-shaped tripwire prints its own remedy, so following its
  instructions verbatim is how a wrong row gets past the suite.

The generalisation for the next reader: **a documented expected-UNDETECTED is a
claim with an expiry date, and nothing was checking it.** If you add one, say
what would have to change for it to close, and re-measure it when that changes.

## Sabotages NOT encoded here, and why

Two sabotages documented in `tests/codegen/CLAUDE.md`'s `run_trie_identity.sh`
table are deliberately absent from `sabotages/`:

- **The naive rule-1 sabotage** ("skip the accept split, change nothing
  else"). The table itself says not to use it: it leaves items with
  `len == depth` in the list for rule 2, which then reads past the allocated
  key — a 32-byte arena over-read, so the failure count is UNSTABLE between
  builds (171 and 176 observed for the same edit). This tool refuses to encode
  a sabotage whose own documentation says its count is not reproducible;
  encoding it would print a number that looks authoritative and isn't.
- **The memory-safe replacement rule-1 sabotage** ("hoist every accept to the
  front instead of partitioning the list around each, keep removing them from
  the list"). This is a real, encodable edit, but the table describes it in
  PROSE — a restructuring of `trie_build`'s rule-1 loop in `src/ir/nfa.c`
  (around the `has_acc` block) — not as literal before/after text. Every other
  row in every sabotage table in this project IS literal text, which is what
  makes `lib/replace.py`'s anchor mechanism honest: it can assert the edit
  landed because it knows exactly what "landed" means. Turning this one
  sabotage into a literal patch would mean writing the actual accept-hoisting
  C code myself and asserting *that specific rewrite* landed — a choice with
  more than one honest implementation, unlike every other row here. Left for
  whoever touches `trie_build` next to encode alongside the code change, the
  way the project's convention already asks ("add its check here in the same
  change").

One sabotage was ADAPTED rather than copied literally: `S15-drop-d-row`
translates `tests/reject/CLAUDE.md`'s "drop `{'d', \"classes\"},` from
`esc_modules`" — `esc_modules` as a distinct table no longer exists; the SR-2
registry refactor folded it into the `ESC(...)` rows in `src/parse/registry.c`
that `S16`/`S17`/`S19` already sabotage. The functionally equivalent edit
today is deleting the `ESC('d', ...)` row outright, which is what `S15` does.

## Conventions

Anchors are copied from `git show HEAD:<path>`, not from a live working-tree
read — this repository routinely has other in-flight work editing the same
files this tool sabotages, and `run_sabotage_matrix.sh` always measures
committed HEAD via `git archive` regardless of what the working tree looks
like at run time. When source drifts enough that an anchor's occurrence count
changes, the run fails LOUDLY on that one sabotage (`APPLY-FAILED`, anchor
mismatch reported by `lib/replace.py`) rather than silently applying to the
wrong place or skipping. Re-derive the anchor from `git show HEAD:<path>` when
that happens; do not weaken the count check.

Maintenance: when a codegen/reject/trie sabotage table gains a new row with an
exact literal edit, add a matching `sabotages/S<NN>_*.sh` here in the same
change, per the project's own sabotage-validation convention.

## [ENG-BREP] S45-S49, and the row that came back green

Five sabotages for the possessification rung, one per rule the design records
as REFUTED — S45 the lazy conjunct, S46 (U1) one-unambiguity, S47 (U2)
prefix-freeness, S48 the enclosing-loop FOLLOW term, S49 the assertion
exemption leaking from `$` to `^`. They run the new `possdiff` arm
(tests/possessify/run_possdiff.sh), which is the only suite that can see a
wrong possessification verdict: a quantifier the analysis admits unsoundly
still matches correctly on most subjects, so the signal is a DIVERGENCE
between the two builds, not a corpus failure.

**S48 is the row that earned this directory its keep.** It came back
UNDETECTED on its first run — and the finding was about the POPULATION, not
the term: every nested cell in the differential's pattern file put a
NON-NULLABLE item after the inner quantifier, a shape where the enclosing-loop
term is merely conservative. A generated search over an 18,480-pattern nested
family then found 7,553 patterns whose verdict changes without the term and 44
WRONG SPANS in a 1,259 sample, the discriminating shape being an inner
quantifier at the END of the enclosing body. Twelve witnesses were added and
S48 is now DETECTED. This is exactly what the driver's own banner says a green
row means: not a bug in the script, the finding it exists to surface.

## [ENG-BREP] S50-S52, the reverse-deterministic rung's controls

Three sabotages for the ladder's second rung, on the same argument S45-S49 rest
on one rung up: a rung selected on an unsound condition still matches correctly
on most subjects, so the signal is a DIVERGENCE between the rung build and the
`-fno-revdet` (replication, i.e. ground truth) one. They run the new `rungdiff`
arm (tests/rungselect/run_rungdiff.sh).

Each removes ONE thing, because the point is to say which thing is load-bearing:

- **S50** leaves the REVERSE DIRECTION unchecked and keeps the forward one.
  This is the sabotage the rung's name is about — forward determinism makes the
  SCAN work, reverse determinism is a separate property and it is what makes the
  RETREAT computable locally. Its witness is `(?:ab|b)`, which passes forward
  and is ambiguous reversed.

  **It came back green in its first form, and the finding was NOT about the
  population.** That version removed only the reverse unique-iteration test and
  measured 0 divergences over 201 patterns — with the discriminating body
  present. The cause is that `rd_alt_disjoint`, which the same pass runs on the
  same reversed tree, independently declines the same family: over the shapes
  this rung admits, reverse ambiguity always presents as an alternation whose
  branches share a first byte. So the two reverse-direction checks are MUTUALLY
  REDUNDANT there, and the row is now stated as the property that is actually
  load-bearing. Removing both diverges at once. The full account, including when
  the redundancy would end, is in
  `docs/design/rungselect_impl/rungselect_design.md` §1.0.1.

  Worth putting beside S48: that row was green because the population could not
  reach the defect, this one because the thing it removed was not the thing
  carrying the weight. Both are findings; they are different findings, and only
  running the row tells you which.
- **S51** removes the forward scan's per-ITERATION cut. It produces no wrong
  answer on a short subject, which is exactly why it needs a control rather than
  trust: the leftover frames are dead by the verdict, so re-entering one cannot
  change the result. What it produces is frame exhaustion below the length the
  artifact stamps, caught by the differential's FAILURE-SURFACE comparison —
  §5.1's third item, and the one a weaker check would drop.
- **S52** defeats the backward capture walk's first-seen-wins guard, so a group
  reports the EARLIEST iteration that entered it instead of the latest. That is
  precisely the clause eng_brep_design.md §3.4 records the plan row getting
  wrong on 1,799 of 15,036 matches, and it is the only one of the three whose
  signal is visible in the `.rxt` corpus as well as in the differential — so it
  carries both arms, which is also a check that the corpus is not merely
  decorative.

## [ENG-BREP counter-K] S53-S57

The counter rung's five rows, running the `counterkdiff` arm. They are not
written up here; read the definitions in `sabotages/`, which carry their own
reasoning. Noted rather than silently absent, because a reader counting
sections would otherwise conclude the rung has no controls.

## [M4.6d] S58-S63, MRL pruning's controls — and the arms are ASYMMETRIC

Six rows for a mechanism that is not a rung: MRL emits a length bound ON
whichever rung a quantifier already took. They run two new arms, `mrldiff`
(tests/mrl/run_mrldiff.sh) and `mrl` (tests/mrl/run_mrl_tests.sh), and the
reason there are two is the thing to understand before reading any verdict.

**A differential is STRUCTURALLY BLIND to half of this mechanism's failure
modes, and that is a property of the bound rather than of the population.**
`minrest` is a LOWER bound on what an accepting continuation still consumes.
Under-estimating it — or losing it entirely — prunes LESS, changes NO answer,
and leaves the pruned and denied builds agreeing on every cell. What it
changes is the STEP COUNT. So no pcrec-vs-pcrec comparison can see a bound
that quietly stops existing, however many cells it compares; only an
acceptance cell that reads the step count can. That is why `tests/mrl/` has
both instruments and why these rows split cleanly between them:

- **S58** makes `pcrec_minw` report 0 for a byte class — every follow-min
  collapses, no bound is emitted anywhere, and the artifact is pre-MRL pcrec
  byte for byte. **MEASURED: `mrl` 14 fail / 4 pass, `mrldiff` 0 fail / 146
  pass.** That green differential column is not a gap; it is the asymmetry
  above, measured instead of argued, and it is the strongest single answer to
  "why does this directory need acceptance cells when it already has a
  202,458-cell differential".
- **S59** makes `minw` report a bounded repeat's MAXIMUM — the UNSOUND
  direction, the one that deletes real matches. Carries `mrldiff harness`,
  because an over-estimate is exactly what a differential and a corpus CAN
  see and an acceptance cell cannot.
- **S60 is the row that changed shape twice, and both changes are findings.**
  Its first form restored R26 E1 — the clamp without its lattice rounding —
  and came back UNDETECTED at `mrldiff 0 fail / 146 pass`, `mrl 0 fail / 19
  pass`. Not a thin population: **the shipped emitter cannot express that
  defect.** §4.1 rounds because the clamp ASSIGNS a cursor value; this emitter
  never assigns one, it FOLDS the cap into the scan's own bound, and `cur`
  only ever moves by `W` from `pos`, so the loop bound is SELF-ROUNDING and an
  off-lattice cursor has no spelling (verified by hand, rounded vs unrounded
  identical on a stride-2 shape at n = 198..201). The rounding stays in the
  emitted macro so a future site that does assign from it is correct by
  construction, but it carries no weight today and a row pretending otherwise
  would be a green check nobody could read.

  Rewritten to what IS load-bearing there — the UNDERFLOW GUARD in front of
  the cap, without which `ceil - minrest - pos` wraps and the folded scan
  bound stops bounding the subject. **It came back UNDETECTED a second time**,
  and that was a third finding: the defect is UNDEFINED BEHAVIOUR (measured as
  an ASAN heap-buffer-overflow), not a wrong answer, so no subject sweep
  reliably reaches it and the mech matrix has no sanitizer arm. The check it
  now defeats is therefore STRUCTURAL — `run_mrl_tests.sh` §2b asserts the
  guard macro carries both clauses and that no artifact has more cap sites
  than guard sites. **DETECTED, `mrl 1 fail / 20 pass`.**

  Put beside S48 (green because the population could not reach the defect) and
  S50 (green because the thing removed was not the thing carrying the weight),
  this row is a third kind: green because the defect it described does not
  exist in the shipped form, and then green again because the real defect is
  invisible to the arms this matrix runs. Only running the row tells you
  which, which is the whole argument for the directory.
- **S61** deletes ONE rung's clamp (the greedy cursor's fold into its scan
  bound) and leaves every other rung's bound intact, including the stamp. S58
  removes the analysis and every rung loses together; this says which rung's
  emission carries K23. **MEASURED: `mrl` 8 fail / 11 pass, `mrldiff` 0 fail /
  146 pass — the same asymmetry S58 shows, one rung down.**
- **S62** is the defect this lane actually shipped first, restored so it
  cannot return unannounced: the counter rung's per-copy follow-min drops its
  runtime term and keeps the within-trip constant. Nine bytes of visible
  follow on `(a{1,3}){65}` where the truth is 65. It carries the `mrl` arm
  ALONE, and that is the honest statement of what found it: the differential
  agreed with the bug, the corpus had no such shape, and the §1 acceptance
  cell uses an exemplar that reaches its collapse through a different rung.
  **MEASURED: `mrl` 2 fail / 17 pass — and the two failures are §1b's own
  cells, which is the narrowest signal in this set and the reason that cell
  was written.**
- **S63** carries the stale prefilter window across the `start++` retry —
  D51 ruling 2 (b), whose error direction is too SMALL, i.e. unsound. No
  subject sweep reliably reaches the state (the retry is argued unreachable on
  the prefilter path, and a critic could not make it fire in 99 trials), so
  the check it must defeat is a STRUCTURAL assertion that the recompute exists
  in the emitted C. This row is what proves that assertion can go red.
  **MEASURED: `mrl` 1 fail / 18 pass.**

## [M4.6f] S64-S65, the PREFILTER axis's controls

Two rows for D46's close-out on `fit.prefilter` (src/opt/select_engine.c,
engine_m4.md §6.1/§4.7): the `RX_VM_PREFILTER` stamp and the
`-fprefilter`/`-fno-prefilter` force pair (lib/pcrec.h). They run the new
`prefilter` arm (tests/prefilter/run_prefilter_tests.sh) — its own arm for
the same reason `vmidentity`/`irlisting` are separate from `codegen`: what
this suite guards (the stamp agreeing with the actual emitted `_prefilter()`
machinery, the do-or-die refusal, the `rx_info.flags` mask) is orthogonal to
`vm`/`mrl`, and a sabotage of one must not be reported as coverage by
another.

**Both rows started as AD-HOC dev-time sabotages, applied and reverted by
hand during the lane, and were converted to permanent rows before handback
per R28-1's ruling** (`docs/dev/reviews/2026-08-17-r28-mrl-landing.md`: MRL
landed with zero sabotage coverage despite having ad-hoc-validated its
checks the same way, and the panel required S58-S63 be authored as the
fix — the same requirement applied here on the same session's later
ruling, before this row's own handback rather than after a panel had to
say so).

- **S64** removes the FORCE-ON do-or-die refusal itself
  (`if (force_on && fit.chosen != ENGM_VM) ctx_fail(...)`), so
  `--engine=dfa -fprefilter` and `--no-captures -fprefilter` compile
  SUCCESSFULLY instead of refusing. What actually happens on the sabotaged
  tree is worth recording rather than assuming: `fit.prefilter` is set
  `true` unconditionally on the force-on path, but nothing on the DFA
  emission path ever reads that field (`compile.c`'s DFA-pair build guard
  already fires whenever `fit.chosen == ENGM_DFA`, independent of
  `fit.prefilter`, and `emit_dfa.c` — the emitter that actually runs — has
  no consumer for it at all), so the artifact compiles and is byte-for-byte
  an ordinary unforced DFA build. The silent-honour failure mode is
  therefore invisible to every other check in the tree: the emitted C is
  unchanged, so no corpus, differential or byte-identity gate anywhere can
  tell a refused request was silently granted. **MEASURED: `prefilter`
  2 fail / 16 pass** (the two do-or-die refusal checks).
- **S65** drops `PCREC_NO_PREFILTER`/`PCREC_FORCE_PREFILTER` from
  `emit_info_def`'s `strategy_denials` mask (src/gen/emit_dfa.c), so the two
  force-pair bits leak into the emitted `rx_info.flags` literal even though
  the axis changes no match behavior. No correctness check anywhere sees
  this — the .rxt corpus, the vm_oracle sweep and the §3.7 differential all
  still agree, because the MATCH BEHAVIOR really is unchanged; only a check
  that reads `rx_info.flags` as a NUMBER against the bit values, rather than
  trusting the mask is complete, can see the leak. **MEASURED: `prefilter`
  4 fail / 14 pass** — the two direct mask-value checks, plus (as a side
  effect neither row's author predicted going in) the two byte-identity
  checks, since the leaking bit is exactly the byte difference those exist
  to rule out.

Both validated DETECTED via `bash tests/mech/run_sabotage_matrix.sh S64`
and `S65` before landing.

## [OPT-ALTCLS] S66-S67, the ALTERNATION -> CLASS NORMALIZATION controls

Two rows for `src/opt/altcls.c` (docs/dev/plan.md's `[OPT-ALTCLS]` row),
running two new arms: `altdiff` (tests/altcls/run_altdiff.sh, the pass live
vs. `-fno-altcls-merge -fno-altcls-factor` differential) and `altcls`
(tests/altcls/run_altcls_tests.sh, the structural checks). Their own arms
for the reason every differential/structural pair in this matrix is split:
what each guards is orthogonal to `possdiff`/`prefilter`/etc., and a
sabotage of this pass's rewrite must not be reported as coverage by another
pass's checks.

- **S66** removes stage 1's UNION LOOP — the merged class keeps only its
  FIRST branch's bitmap instead of OR-ing every branch in the run into it.
  `b|c` silently compiles to `[b]`, deleting the `c` alternative from the
  language entirely: a real miscompile, not an invented one, and the shape
  every soundness argument for a class-merging pass has to get right first.
  `RX_ALTCLS_MERGES` still stamps 1 (the merge event fires; only the union
  is wrong), so nothing observability-shaped sees it — it needs a check
  that exercises the merged class against a subject only the DROPPED branch
  could match, which `run_altdiff.sh`'s per-pattern-character subject sweep
  (D47.6's rule) does by construction. **MEASURED: `altdiff` >0fail** (the
  `b|c`-shaped patterns in `patterns.txt` diverge on the `c`-only subject).
- **S67** drops `PCREC_NO_ALTCLS_MERGE`/`PCREC_NO_ALTCLS_FACTOR` from
  `emit_info_def`'s `strategy_denials` mask (src/gen/emit_dfa.c) — the S65
  shape one pass over. The two deny bits leak into the emitted
  `rx_info.flags` literal even though the axis changes no match behavior;
  no correctness check anywhere else sees it, because the match behavior
  really is unchanged (`altcls.rxt` and `run_altdiff.sh` both still agree).
  Only `run_altcls_tests.sh`'s byte-identity check (pass-on vs. pass-off on
  a verdict-free pattern) reads the leaking bit as the byte difference it
  exists to rule out. **MEASURED: `altcls` >0fail** (the byte-identity
  check and the direct do-or-die/no-trace stamp check both move).

Validate with `bash tests/mech/run_sabotage_matrix.sh S66` and `S67`.
