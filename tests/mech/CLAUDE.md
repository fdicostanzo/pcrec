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
- **rows_for.sh** ([TT-8], 2026-08-23) — lists the `SAB_ID`s whose
  `SAB_FILE`/`SAB_FILE2`/`SAB_HARNESS_TARGET` matches one or more given
  paths, at a path-component boundary. What D69's tiered re-run policy
  (below) needs to answer "which rows" for a changed-files list without a
  hand read of `sabotages/`. A path matching no row prints nothing and
  exits 0 (success, not failure — it means the anchor tripwire alone
  covers the change); a malformed definition (missing `SAB_ID`/`SAB_FILE`)
  is a FATAL exit 2 naming the file, never a silent skip. Does NOT match a
  full-corpus `harness` row (no `SAB_HARNESS_TARGET`) against an unrelated
  path — see its own header for why that is deliberate rather than a gap.
- **sabotages/S\*.sh** — one file per sabotage, sourced by the driver. Sets
  `SAB_ID`, `SAB_FILE`, `SAB_SUITES` (space-separated: `codegen` `trie`
  `reject` `harness` `registry` `pc3` `cli` `vmidentity` `vm`
  `endvaridentity` `assertions` `kresetdiff` `lookaround` `laexpand`, plus the
  per-lane arms listed below),
  `SAB_DESC`,
  `SAB_BEFORE`, `SAB_AFTER`, and optionally
  `SAB_COUNT` (default 1), `SAB_HARNESS_TARGET` (an .rxt file or dir to
  scope the `harness` suite to, instead of the whole corpus), and
  `SAB_EXPECT` (see below). Each file also
  carries `SAB_DOC_FIGURE`, a comment-and-string record of what the source
  documentation claimed, purely for humans diffing a re-run against the docs —
  the matrix itself does not read it.

## `SAB_EXPECT` — THE EXPECTATION, CHECKED ([DD-14] wave B+C)

`SAB_EXPECT` is `DETECTED` (the default when absent) or `UNDETECTED`. The
driver scores every row against it, the headline reads **`unexpected: N`**,
and **a mismatch in either direction exits non-zero.**

**WHY IT EXISTS.** This directory already learned this lesson and wrote it
down at S19 — *"a claim with an expiry date, and nothing was checking it"* —
after a documented expected-UNDETECTED row had quietly BECOME detected and
nobody noticed for weeks. The prose remedy ("a hand-maintained expected-
UNDETECTED is precisely the staleness this directory records") did not
survive contact with the next wave that needed one: [DD-14] wave B+C shipped
SEVEN rows whose expectation lived only in a paragraph. This field is that
paragraph made executable, and the rule generalises past those seven —
**an expectation a human maintains in prose is a claim; an expectation the
runner checks is a contract.**

The two mismatch directions are BOTH findings and both fail the run:

| stated | measured | meaning |
|---|---|---|
| `DETECTED` | UNDETECTED | a guard regressed, or the row's population was never adequate. The original finding, unchanged. |
| `UNDETECTED` | DETECTED | **`NOW DETECTED`** — the claim EXPIRED: a later wave grew the population that closes the row. Re-measure, then flip the field. |

That second row is deliberately the `known_fail` ratchet's *"now passing"*
shape: the correct response is a deliberate re-measurement, **never deleting
the row and never leaving the stale expectation standing**. An
expected-UNDETECTED row is therefore not a parking space for a dead sabotage
— it is a claim with a named witness that would close it, recorded in that
row's `SAB_DOC_FIGURE`.

**`INCONCLUSIVE` and `ANOMALY` are scored against NEITHER expectation.** They
are the ABSENCE of a measurement, and an absent measurement must never satisfy
a stated one — the same reason a skipped oracle arm is not a pass. A typo'd
value (`UNDETECED`) is a hard `FATAL` rather than a silent fall back to the
default, because falling back would turn a checked claim into an unchecked one
and reintroduce exactly the failure this field was added to fix.

## THREE SUITE NAMES THE `[DD-14]` DESIGN ASSUMED, AND NONE OF THEM EXISTS

`subroutines_design.md` §9.3 assigns three of its rows to suites this
directory does not have: S-SR9a and S-SR11 are described as **"a TIMEOUT
row"** with *"`tests/mech/`'s timeout suite is the assignment"*, S-SR19 is
*"`asan`-suite as well"*, and one row named `rungselect` (the test
DIRECTORY's name) where the arm is `rungdiff`. The `*)` arm scores an
unrecognised word as `UNKNOWN-SUITE` rather than silently ignoring it, which
is how all three were caught on their first run.

**THE HANG ROWS ARE `harness` ROWS, and that is not a demotion.**
`tests/harness/run.sh` runs BOTH the `pcrec` invocation and the compiled
matcher under `TIMEOUT_BIN` (with the budget from `tests/lib/gen_timeout.sh`,
D45), and a non-zero exit — timeout included — is scored a FAILURE naming the
case. So a compiler that does not terminate on `(a(?1))`, or a matcher that
pushes and cuts at zero consumption for ever, is a red harness case rather
than an infrastructure event. What the design wanted from a "timeout suite" is
what `harness` already does; what it does NOT have is a way to say *"this row
is EXPECTED to time out"*, and neither would a separate arm.

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
- `endvaridentity` → `tests/codegen/run_endvar_identity.sh`, [M6.2] wave A's
  byte-identity gate. Its own arm rather than `codegen` or `trie`, for the
  reason `vmidentity` is its own: "adding a THIRD closure view moved no byte
  of any pattern that does not use it" is orthogonal to every
  optimization-present check and to the trie's own equivalence. It builds a
  reference compiler and sweeps the whole corpus, so it is the most expensive
  arm here — assign it only where the signal really is emitted bytes.
- `lookaround` → `tests/lookaround/run_lookaround_diff.sh`, module
  `lookaround`'s behavioural instrument ([M6.6.2] wave B+C). Its own arm, and
  wired at wave B+C rather than at wave F where the design placed it (R33
  C2-7), because two of that wave's own rows cannot be scored without it.
  **What it sees that no other arm can is a DISAGREEMENT**: `(?=` and `(?*`
  differ in exactly one emitted line, so §2 asserts the EXACT number of cells
  on which the two spellings must answer differently — a compiler that cut
  both, or neither, reports agreement where 13 disagreements are required, and
  an arm that only checked each spelling against libpcre2 would go green on
  BOTH S122 and S131. §1 re-drives every `# pcre2-only` cell in the corpus
  against libpcre2, which for `nonatomic_ahead.rxt` is the only oracle those
  cells have (python has no `(?*` at all). SKIP-is-not-a-pass exercised in the
  failing direction as `pc3` was.
  **WAVE D TRIPLED ITS §1 POPULATION, 14 -> 44 answer-bearing blocks / 4,268
  cells**, because `lookbehind_widths.rxt` and `nonatomic_behind.rxt` are
  `# pcre2-only` in their ENTIRETY (python refuses differing-width lookbehind
  alternatives outright, and has no `(?<*` at all). §2's exact disagreement
  count stayed 13 across a subject-set growth of 19 -> 26, which is the only
  kind of evidence an exact literal can give that it measures what it names.

  **AND ITS §1 SWEEP IS BOUNDED BY A SHARED SUBJECT SET, WHICH IS A COVERAGE
  FACT AND NOT A DEFECT.** All three sections drive a SHARED 19-subject list
  drawn from the corpus's own alphabet, so §1 does not re-drive a pcre2-only
  block's OWN subjects — it re-drives its PATTERN over those nineteen.
  MEASURED at wave E: S140 turns `tests/lookaround/prefilter.rxt` red at
  31fail/22pass and leaves this arm at 0fail/5pass, because not one of the
  nineteen subjects contains a `q` and the hazard the row is about is
  therefore unreachable here. **When a row's detector is a specific subject,
  the `.rxt` file is the detector and this arm is not** — assign both, but do
  not read the assignment as coverage.
- `recursion` → `tests/recursion/run_recursion_diff.sh` ([DD-14] wave B+C),
  and it is wired at the wave that BUILDS it rather than at the module's
  close, because two of that wave's own rows are unscoreable without it.
  **S158 lives on the `--no-captures` AXIS, for which no `.rxt` directive
  exists anywhere in this tree** — the corpus is structurally blind to it,
  which the corpus's own CLAUDE.md records as an owed gap — so §1 compiles
  under the flag and reads the ARTIFACT's slot legend as well as the answer.
  **S154's halved trail charge changes NO ANSWER until a capacity is
  crossed**, and a corpus cell has to pick a subject LENGTH in advance; §2
  BISECTS for the artifact's own ceiling instead and asserts that one step
  past it the answer is a TYPED GIVE-UP rather than a wrong `nomatch`, which
  holds at whatever the ceiling is.

  **IT SKIPS ONLY PARTLY, WHICH IS A DIFFERENT SHAPE FROM `laexpand`'s.** Only
  §3 (the libpcre2 subject sweep) needs the oracle; §§1, 2 and 4 RUN
  regardless, so on a box with no libpcre2 the script still prints a real
  non-zero `checks passed:` — never `0fail/0pass`, which is the reading that
  would let a row be called UNDETECTED by an arm that never ran. That is why
  this arm needs no SKIP-banner special case of its own.

- `laexpand` → `tests/lookaround/run_expansion_diff.sh`, the SUBSTITUTION
  DRIVER ([M6.6.2] wave E2, design §6.3). **A different KIND of net from
  `lookaround` above, and the difference is what decides which rows it is
  assigned to.** That one runs the module's own ~175-block corpus — BREADTH,
  every spelling and every body shape. This one re-expresses
  `tests/assertions/`'s 8,260 libpcre2-verified cells as lookarounds and drives
  887 generated patterns through a THREE-WAY check per cell (pcrec on the
  expanded pattern, pcrec on the FOLDED one, libpcre2 on the expanded one) —
  DEPTH, over exactly the body shapes the assertion family uses, which is one
  class or one literal. It brings 2,943 NONZERO-STARTPOS cells with it for
  free, which is the axis §3.8's contract lives on.

  **THE ROWS IT IS NOT ASSIGNED TO ARE AS MUCH A RESULT AS THE ONES IT IS**, and
  both were MEASURED before anything was assigned — see the wave E2 section
  below for the 15-row table. Every expansion in §6.1's table is an ATOMIC
  lookaround with a FIXED-WIDTH body, so a sabotage of the non-atomic flag
  (S131) or of the lookbehind width rule (S136) is invisible here HOWEVER MANY
  CELLS RUN. Assigning this arm to those rows would have bought a bigger
  denominator and no evidence — the shape this directory exists to refuse.

  SKIP-is-not-a-pass exercised in the failing direction as `pc3` was; it is the
  SECOND arm here that can decline for want of an oracle, and the verdict block
  now NAMES the arms that skipped instead of assuming `pc3`.
- `assertions` → `tests/assertions/run_assertions_tests.sh`, module
  `assertions`' structural checks (the libpcre2 re-verification of its
  corpus, the built-constructs control, and the D47.5 exemption read off the
  artifact's STRATS stamp in both directions).

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

## TWO arms can SKIP, and a skip is not a pass

`pcre2_check.c` dlopens libpcre2 and exits 0 with `SKIP:` lines when it is
absent — the convention that keeps a stranger's clone green. The arm reproduces
that as a **visible `pc3:SKIPPED-no-oracle` cell**, never as a silent zero, and
the verdict logic refuses to let it read as evidence:

- a row whose assigned suites ALL skipped is `INCONCLUSIVE`, never
  `UNDETECTED` — the latter is a finding, and it would be a false one;
- a row that ran something else carries `(pc3 SKIPPED -- no oracle)` appended
  to its verdict, because "caught by nothing" means something different when
  one of the nets was not in the water. **Since [M6.6.2] wave E2 the suffix
  NAMES the arms that skipped** rather than assuming `pc3` — with one skipped
  arm it renders exactly as it always did, and with both it reads
  `(pc3 laexpand SKIPPED -- no oracle)`;
- the end-of-run summary lists every skipped row, and the completion trailer
  counts them: `== mech run COMPLETE: N rows (undetected: U, anomalies: A,
  oracle-skipped: S) at <SHA> ==` (the field was `pc3-skipped:` before wave E2,
  when `pc3` was the only arm that could produce it).

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

**AND ONE SABOTAGE ROW IS OWED BY A DIFFERENT DELIVERABLE ENTIRELY.**
`S-SR2a` (subroutines_design.md §9.3) sabotages the fail label's restore of
`call_depth` — the recursion-depth COUNTER. **It is not written, and wave F
did not write it, because the thing it sabotages IS NOT IN THE DEFAULT
ARTIFACT**: D71 item 1 ruled the counter a DIAGNOSTIC GENERATION AXIS in
`[V-H]`'s namespace (`--trace`'s shape, a separate emitted variant the
artifact stamps, never a runtime flag), emitted only when the post-discharge
tree contains a call. A sabotage row against a field no default artifact
carries would be UNDETECTED for a reason that is not a finding.

So the row is **OWED BY `[V-H]`'s AXIS**, and it lands with it: when the
diagnostic variant ships, S-SR2a's detector is the codegen count of the
restore site PLUS a deep-recursion cell that must still reach its answer
(a leaked `call_depth` makes `RX_CALL` refuse early, which no answer-based
check sees). Recorded here rather than in the design so the next person to
open this directory looking for the row finds out why it is absent —
this file's own standing rule about a claim with no checker.

One sabotage was ADAPTED rather than copied literally: `S15-drop-d-row`
translates `tests/reject/CLAUDE.md`'s "drop `{'d', \"classes\"},` from
`esc_modules`" — `esc_modules` as a distinct table no longer exists; the SR-2
registry refactor folded it into the `ESC(...)` rows in `src/parse/registry.c`
that `S16`/`S17`/`S19` already sabotage. The functionally equivalent edit
today is deleting the `ESC('d', ...)` row outright, which is what `S15` does.


## [M6.4.2] S88-S100, and a SELECTOR COLLISION this numbering made real

Thirteen rows for module `atomic-groups`, and two things about them are worth
reading before adding a fourteenth.

**THE SUITE WORDS HAD TO BE REGISTERED FIRST.** `run_sabotage_matrix.sh`'s
suite vocabulary is CLOSED — an unrecognised word scores `UNKNOWN-SUITE` — so
FOUR of these rows (S91, S92, S96, S97) could not have been SCORED AT ALL until
`atomicdiff` existed. R31 C11 named that as a blocker rather than a detail, and
the design's slice ordering makes the registration PRECEDE the sabotage
measurement. `atomicidentity` was registered with it.

**EVERY ROW'S `SAB_BEFORE` WAS VALIDATED TO OCCUR EXACTLY `SAB_COUNT` TIMES IN
ITS FILE, AND TWO DID NOT.** S88 matched a `\\n` where the source has `\n`, and
S89 was a guess at emitted macro text; both were rewritten from the source
itself. A row whose `SAB_BEFORE` matches nothing is a row that measures
nothing, and it is the one defect in a sabotage definition that produces no
error anywhere until somebody reads the count.

**THE SELECTOR HAD A LIVE PREFIX COLLISION, and R31 C4 named its shape a
numbering ago.** The row filter was `[[ "$base" != "$ONLY"* ]]` — a bare prefix
match on the basename — and C4 caught a proposed `S87` colliding with the
shipped `S87_kreset_trail_uncharged.sh`: *"the driver's ID-prefix match would
have selected two `S87-` rows."* [M6.4.2] took the numbering past two digits
and made the same hazard REAL for the first time: with `S100_lift_accepts_
nullable.sh` on disk, `run_sabotage_matrix.sh S10` selected BOTH it and
`S10_casefold_one_direction.sh` — two unrelated rows, one intended, and a
figure attributed to whichever finished last. Measured on this tree before the
fix. The match is now at the ID BOUNDARY (a basename is `S<id>_<name>.sh`, so
the boundary is the underscore): `S10` selects `S10_*` and nothing else, and
`S1` selects nothing, which is right — it is not an id.

**S100 IS THE ONLY ROW IN THE TABLE WHOSE FAILING DIRECTION IS NOT AN ANSWER.**
Removing the lift's nullability carve-out routes a nullable body onto
`vm_poss_star`, which emits no empty-iteration guard, and the emitted matcher
pushes and cuts at ZERO CONSUMPTION forever. Its expected result is a TIMEOUT —
which D45's generated-matcher execution budget makes a loud failure naming the
case rather than a hang, and without which the row would be unscoreable.

## [M6.5.2] S102-S120, NINETEEN ROWS, AND THE ID SPACE'S FIRST REAL COLLISION

Nineteen rows for module `backrefs`, and four things about them are worth
reading before adding a twentieth.

**THE SUITE WORDS WERE REGISTERED FIRST, DELIBERATELY.** `brefdiff`,
`dupnamesdiff` and `brefidentity` went into the vocabulary and got their arms
BEFORE any row named them, because the vocabulary is CLOSED and eight of these
nineteen would otherwise have scored `UNKNOWN-SUITE` — which is not "failed",
it is "not measured". That is R31 C11's lesson applied rather than
rediscovered.

**S100 AND S101 WERE ALREADY TAKEN**, by `S100_lift_accepts_nullable.sh` and
`S101_follow_crosses_cut.sh`, so this module's rows start at S102. The first
draft of them did not check, and the collision would have been silent in the
worst way: two files with the same id, `SAB_ID` strings disagreeing with their
basenames, and the ID-boundary selector (fixed one numbering earlier) selecting
whichever the glob reached first. **Check the highest existing id before
numbering a block of rows**; `ls tests/mech/sabotages | sed 's/^S\([0-9]*\)_.*/\1/' | sort -n | tail -1`
is the whole procedure.

**EVERY `SAB_BEFORE` WAS VALIDATED TO OCCUR EXACTLY `SAB_COUNT` TIMES, and one
row had a defect no anchor check could see.** S115's `SAB_DESC` contained a
BACKTICKED word inside a DOUBLE-QUOTED string — a live command substitution
the moment the matrix sources the file, which bash reported as a syntax error
in the middle of an unrelated `$( )`. The anchor was fine; the row was not.
Single-quote `SAB_BEFORE`/`SAB_AFTER` (they already are, for `$` and `\`) and
keep backticks out of the double-quoted fields.

**FOUR ROWS OF SOMEBODY ELSE'S WERE RE-ANCHORED**, and the tripwire is what
said so — it was RED on arrival at this lane with S10, S22, S26 and S94 all
stale, every one from this lane's own ordinary edits (`cls_casefold` rewritten
to derive from a shared fold table; `(?^)` gaining a second preserved letter;
the option set/unset block gaining `set_J`/`un_J`; a new declining arm landing
between `A_ATOMIC`'s and `A_CAP`'s in `rd_shape`). All four were re-derived
FROM THE LIVE SOURCE. **S10's re-derivation changed the sabotage's SHAPE** —
its old anchor was a two-armed `||` that no longer exists — so its INTENT was
re-verified by APPLYING it: with the row live, `-i '[A]'` stops matching "a"
and still matches "A", which is the one-direction fold the row is named for. A
re-anchored row whose intent nobody re-checked is a row that measures something
else.

**THE ROW WHOSE FAILING DIRECTION IS NOT AN ANSWER IS S107** (`vm_nullable`
false for `A_BREF`), and its detector is the harness's derived TIMEOUT: a
reference whose group published an empty capture consumes nothing, so a
quantifier over it loses its empty-iteration guard and loops forever. **The row
whose failing direction is not a REFUSAL either is S102** (a prefilter planted
on a backref pattern) — it changes a SPAN, on a population that is invisible
unless the erasure's window fails to CONTAIN the true match, which is why
`run_backref_diff.sh` §8 exists and asserts its three subjects exactly.

**AND S109 IS THE S68 SHAPE ONE CONSTRUCT OVER**: inlining the backreference
compare instead of routing it through the encoding seam changes NO ANSWER under
the byte backend, so every corpus and every differential stays green. Its only
possible detector is the codegen check's fixture-DECLARED per-site call count.

## [M6.4.4] S101, THE ONLY ROW IN THE TABLE WHOSE DEFECT SHIPPED

Every other row in this directory re-introduces a defect that was caught
before it landed, or one that never existed outside the row. **S101 undoes a
fix for a defect that was live in main** — `(?:aa|a)++ab` answering (0,4) on
"aaab" against libpcre2's and python's NO MATCH, from [M6.4.2]'s merge
(`69f3b93`) until [M6.4.4]. The blinded D27 corpus found it; 748 corpus cases
and a 39,326-cell x 3-arm differential had been green over it.

That makes the row's *scoring* unusually informative rather than merely
confirmatory: it is a direct measurement of the corpus gap that let the defect
through. The suites it should redden are `atomicdiff` (2,484 disagreeing cells
plus 4 follow-barrier failures, measured on the applied tree) and `harness` on
possessive.rxt section 10 (13 cases). The rows it must NOT redden are the ones
whose follows are disjoint from their bodies — which is the whole `cut` class
that existed before, and the reason the gap was invisible.

**AND THE ANCHOR TRIPWIRE EARNED ITS KEEP AGAIN, THREE TIMES IN ONE LANE.**
`scripts/m6read_check_sab_anchors.py` was RED on arrival at [M6.4.4] with
three stale anchors, all from ordinary refactoring in the preceding lane:
S45 (`pss_verdict`'s factoring turned an `else if ... verdict = false` chain
into early returns), S63 (H3's site-2 comment was inserted between the guard
and the `snprintf` the anchor spanned) and S90 (a comment rewrite inside
`vm_atomic` — caused by [M6.4.4]'s own fix, and caught in the same run that
found the other two). All three were RE-DERIVED FROM THE LIVE SOURCE
programmatically rather than hand-transcribed, then verified to apply at
exactly `SAB_COUNT` sites and to build. S90's re-derived form was additionally
checked to still produce its intended defect: the sabotaged matcher SEGFAULTS
on `(?>ab|a)b`, because the cut reads a mark slot that was never written.

**S89, S94 and S97 are the three that matter most**: all three are invisible to
every structural check and are caught only by the corpus or by the engine
assertion. If any scores UNDETECTED the corpus is too small, not the row.
S97 in particular has the "changes no answer" shape — the discharge's output
inheriting the discharged node's stamp leaves every match, capture and refusal
identical and only stops the pattern ever becoming DFA-compilable, so the only
thing that sees it is `check_free_discharge` in tests/registry/.

**The `SAB_DOC_FIGURE` on all thirteen is a marked PREDICTION.** The
implementation lane does not run the matrix (the manager does), so each row
says what it expects and names `run_sabotage_matrix.sh SNN` as the canonical
figure still owed.

## [M6.6.2] wave E — S140/S141, and a row whose population had to be MEASURED

Two rows for design §5.6's prefilter ruling, taken from the END of the id range
(S140/S141) so a concurrent wave-D lane could take ids from the middle without
either lane guessing the other's. **The manager renumbers at merge if the two
ranges met.**

**S140's POPULATION IS THE ONE THING ABOUT THESE ROWS WORTH COPYING.** The row
deletes `&& !pcrec_has_lookaround(root)` from `v.mrl_win`, and it can only
score DETECTED if the corpus holds a pattern that BOTH raises a clamp site (so
the ceiling is live) AND loses a match when it comes back. Neither half is
visible by reading the design: `lookaround_design.md` §5.5 records its own
first sweep reporting **0 qualifying shapes over a space in which 0 was the
only possible answer**, because every tail it tried was nullable and a
nullable-follow bounded repeat raises no clamp site at all. So every clamping
block in `tests/lookaround/prefilter.rxt` was compiled by pcrec at `8720029` —
the tree immediately before the predicate landed — its `RX_VM_PRUNE_CEILING`
read off the artifact, and its matcher run on those exact subjects, before the
row was written. Five shapes qualified out of ten tried. **A sabotage row whose
detector cells were chosen by reading a design rather than by running the
pre-fix compiler is a row that has not been shown to be falsifiable.**

**S141 IS S88'S OTHER HALF, AND THE DESIGN'S FIRST SKETCH HAD IT BACKWARDS**
(R33 C2-10). `v.mrl_win` has FOUR readers — the `--emit-ir` PRUNING
description, the `RX_VM_PRUNE_CEILING` stamp, and the TWO lines that BUILD the
ceiling. The sketch had the row sabotage the STAMP and needing a second site to
do it; the stamp is a one-site expression, so flipping its source needs no
second site. The BUILDERS are the pair that is two sites by construction, so
S141 uses `SAB_FILE2/BEFORE2/AFTER2/COUNT2` to gate both of them on
`job->fit.prefilter` while LEAVING THE STAMP reading the flag. S88 does the
entry site alone, for the atomic module; S141 does entry AND retry.

**IT IS SCORED BY A CHECK THAT IS ONE FUNCTION FOR TWO MODULES.**
`[M6.4-ATOMIC rule 1]` and `[M6.6-LOOKAROUND rule 1]` are two calls to
`ceil_drop` in `tests/codegen/run_codegen_tests.sh`, which asserts on all four
readers; MEASURED, S141 turns exactly `1(a)` red on each — **2fail/77pass, one
failure per module** — with `1(b)`, `1(d)` and both `1c` twins green, and
`irlisting` green because the fourth reader is untouched. That disjointness is
the row's point, and it is S88's own argument one module over.

## [M6.6.2] wave F — S142, and the row exists because THREE of the family
## check's four claims are covered somewhere else and the fourth is not

`check_families` (tests/registry/registry_check.c) is D71 item 3's tripwire
and asserts four things about a family — no dangling `family` reference, no
chain, exactly one canonical member, and members that AGREE on module,
engines and status. Three of those break loudly elsewhere the moment they
break: a dangling reference reaches `la_kind`'s `BAD_ROW` and reddens the
module's corpus; a widened `engines` mask drops the row out of SR-8's
qualifying population and fires `check_engine_capability`'s exact 66/36/36
count; a moved `built` fires the built-status tally's 118 = 70 + 42 + 6.

**THE MODULE AXIS IS WHERE THIS CHECK IS ALONE**, and it is alone for this
repository's signature reason: the parser RENDERS the diagnostic from the row
and tests/reject/'s dump-driven loop READS the same row for its expectation,
so the two agree in unison about a wrong module. The hand-written second
source covers THREE of the twelve alpha spellings by design (one short, one
non-atomic, one long), so S142 sabotages a FOURTH — `(*napla:` — which that
layer genuinely cannot see. `check_feature_module_bijection` cannot see it
either: the sabotage swaps in `M_verbs`, a VALID feature/module pair.

**NOT A `built` SABOTAGE, deliberately.** Flipping a member `unbuilt` does
break the family's AND rule, but it also moves the built-status tally, so the
family check would not be the detector and the row would be measuring
something already measured.

What goes wrong without the check: `--list-families` and the compliance
page's generated index print ONE line per family reading module from the
canonical member, so a disagreeing member is silently overruled in the index
while `(*napla:a)` itself answers "requires module 'verbs'" to a caller — the
precise defect design §8.2 measured at P3 and this wave was built to fix,
restored for one spelling and invisible in the page meant to report it.

**TWO EXISTING ROWS' ANCHORS MOVED IN THE SAME WAVE**, both caught by
`scripts/m6read_check_sab_anchors.py` on the branch rather than by a failed
run: `RegRow` gained a `family` field (D71 item 3) and every macro and
longhand row in registry.c initialises it explicitly, so S110's `ESC_DIGIT`
body now ends `..., NULL}` and S126's longhand AFTER row carries its own
`NULL` rather than relying on a zero default nobody wrote. Neither sabotage
changed; only the text each is spelled against.

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

## SEVEN ROWS' ANCHORS HAD DRIFTED FROM HEAD (found 2026-08-19, RE-ANCHORED 2026-08-21)

Found by the [M6.2] repair slice while checking that its OWN edits had not
moved any anchor. The method is the driver's own: `printf '%s' "$SAB_BEFORE"`
and count that literal in `$SAB_FILE`, which is exactly what `lib/replace.py`
is handed. Seven rows' anchor text was ABSENT from the file it names, so a
full `make mech` scored each of them `APPLY-FAILED` / `ANOMALY (anchor
drifted from HEAD)` — not `DETECTED`, and not `UNDETECTED` either — and a
per-prefix run (`run_sabotage_matrix.sh S85`) never touches a row it does not
name, which is why nothing noticed until a full-matrix run.

All seven were re-anchored by the sabanchors lane (2026-08-21) against this
same file's Conventions recipe — re-derive from the current source, never
weaken the count check — and each was dry-run applied through
`lib/replace.py` directly (the exact mechanism the driver uses) before
landing, confirming a clean single-occurrence match and a syntactically sound
result. Two drift causes account for all seven:

| row | file | drift cause |
|---|---|---|
| S08 casefold-order | `src/parse/parse.c` | `Ctx.mods` struct→pointer (below) |
| S09 casefold-delete | `src/parse/parse.c` | `Ctx.mods` struct→pointer |
| S21 cls-peek-raw | `src/parse/parse.c` | `Ctx.mods` struct→pointer |
| S22 caret-reset-clears-u | `src/parse/mod_modifiers.c` | `Ctx.mods` struct→pointer, `ModState`→`ParseMods` rename |
| S26 unset-applied-first | `src/parse/mod_modifiers.c` | wave C added the `m`/multiline letter to the set/unset block the anchor spans |
| S39 vm-cursor-always-greedy | `src/gen/emit_vm.c` | [M4.6d] MRL replaced the comment the anchor's second line quoted |
| S65 prefilter-flags-mask | `src/gen/emit_dfa.c` | [OPT-ALTCLS] appended two more mask bits after the anchor's tail |

**Five of the seven (S08/S09/S21/S22/S26) share ONE root cause**: [M6.2] wave
A (`src/parse/parse_mods.h`) turned `Ctx.mods` from a `ModState` struct value
into a pointer to an incomplete `ParseMods` (renamed from `ModState`), so
every `cx->mods.FIELD` site in `src/parse/parse.c` and
`src/parse/mod_modifiers.c` became `cx->mods->FIELD`, and every
`ModState ns = cx->mods;`-shaped local became `ParseMods ns = *cx->mods;`.
None of the five sabotages' anchors were re-derived when that landed — a
single struct-to-pointer refactor silently invalidated five rows across two
files at once, which is worth knowing as its own shape: a source-wide
mechanical rename is exactly the kind of change an anchor's literal-text
contract cannot survive without an explicit re-derivation pass.

**S26 additionally predates a real content addition**, not just a spelling
change: [M6.2] wave C added the `m` (multiline) letter's `set_m`/`un_m`
handling to the exact set/unset block this row reorders. The stale anchor
would have flipped only the block's PRE-wave-C prefix, silently leaving `m`
on the correct side of the reordering — re-derivation added the two new
lines in their real position so the flip still reorders the whole block.

**S39's drift is a comment collision, not a code change.** The `if
(a->greedy) {` line the anchor targets never moved; [M4.6d] (MRL pruning)
replaced the comment that used to sit directly beneath it with the MRL clamp
explanation, and the sabotage's second anchor line quoted the old comment
verbatim. The re-derived anchor quotes the MRL comment instead — which
usefully also disambiguates this specific `if (a->greedy) {` (the span-loop
cursor rung) from two unrelated sites in the same file (the frames rung's
retreat, the reverse-deterministic rung) that share the identical first
line.

**S65's is the one the original finding already diagnosed**: its anchor
ended `PCREC_FORCE_PREFILTER;` and `emit_info_def`'s `strategy_denials` now
ends `PCREC_FORCE_PREFILTER |` followed by `PCREC_NO_ALTCLS_MERGE |
PCREC_NO_ALTCLS_FACTOR;` — [OPT-ALTCLS] appended to the mask and S65's anchor
was not re-derived in the same change. The re-anchored version keeps the
trailing `|` so the ALTCLS bits stay attached to the expression; S65 still
drops only its own two prefilter bits (S67 is the separate row for ALTCLS's
own pair).

**Validation status: CONFIRMED** (2026-08-21, at merge). Dry-run
`lib/replace.py` application confirmed each anchor matches its target
exactly once and produces syntactically valid C reproducing the row's
documented intent; then the by-prefix smoke (all seven DETECTED, fail
counts matching each row's documented figures exactly) and the FULL-MATRIX
run both landed clean: `== mech run COMPLETE: 85 rows (undetected: 0,
anomalies: 0, pc3-skipped: 0) at ae6e41f ==` — all seven ANOMALY ->
DETECTED, no other row's score moved, and the two instruments produced
byte-identical per-row counts. Re-derive the anchor from
`git show HEAD:<path>` whenever this class recurs; never weaken the count
check.

The repair slice's own anchor movement, by contrast, was one row and was
re-derived in the same change: S81's line gained `upc_emit_of_class` when the
emitter's knob half landed. See that row's own note.

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

## S68 ([M5-SEAM], 2026-08-18) — a sabotage that changes NO answer

Worth calling out because it is the first row here whose whole point is
that the behavioural suites CANNOT see it. `S68_residual_in_hot_loop.sh`
makes the emitted bitmap prefilter's skip loop advance through
`<prefix>_next_pos` (the encoding residual) instead of `pos++`, which is
the hot-path/encoding coupling DD-12 (7) forbids. Under the byte backend
the two are the same value, so the artifact matches identically: the `.rxt`
corpus, both oracles, the reject table and every byte-identity gate stay
green, and only `tests/codegen/run_codegen_tests.sh`'s structural check
fires. Measured row: `codegen 3fail/41pass, corpus 0fail/56pass`,
DETECTED.

When reading the matrix, treat a 0-fail behavioural arm on THIS row as the
expected result rather than as a gap in coverage — it is what the row was
built to demonstrate.

## [M6.2 wave A] S69-S70, and two new arms

Two rows for module `assertions`' first wave, running the new
`endvaridentity` arm (tests/codegen/run_endvar_identity.sh) and `assertions`
arm (tests/assertions/run_assertions_tests.sh). Their own arms for the reason
every pair in this matrix is split: what each guards is orthogonal to the
others, and a sabotage of one must not be reported as coverage by another.

- **S69** is this directory's fourth row whose edit is a REAL PAST CLAIM
  rather than an invented failure — and the first whose original is a
  DESIGN's, not an implementation's. `assertions_design.md`'s first draft
  canonicalized `\z`'s third closure view against the BASE view and argued
  zero regression from it; R30 finding E3 showed the comparison is against the
  EOL view, and that getting it wrong makes every eol-differing state of every
  `$`-bearing pattern intern a redundant live `endvar`. The sabotage restores
  the refuted form.

  **It is SEMANTICS-PRESERVING, which is the whole point.** The extra state
  duplicates the eolvar state, so every emitted matcher answers identically:
  the `.rxt` corpus, both oracles and every differential in the tree stay
  green, and only the byte-identity gate can see it. That is the S68 shape
  (a sabotage that changes no answer) with a different mechanism, and it is
  the standing argument for landing a construction check even where the prose
  says it cannot fail.
- **S70** deletes the ESCAPE doorway's enabled-but-unbuilt epilogue, so a
  half-landed module answers "requires module 'assertions'" with the module
  already enabled. Nothing behavioural notices — the pattern is refused
  either way — and tests/reject's GATE-CLOSED rows do not notice either,
  because with the gate closed the old sentence is the correct one. Only the
  four `reject_gated assertions` rows can see it. Note the row's own scope:
  the `m` LETTER's refusal is produced per letter in
  src/parse/mod_modifiers.c and keeps its own copy of the rule, so the two
  `(?m)` rows stay green — which is the honest reading of "a letter's module
  is not the dispatching row's".

## [M6.2 wave B] S71-S75, and one more arm

Five rows for `\b`/`\B`, running the new `wordctxidentity` arm
(tests/codegen/run_wordctx_identity.sh) alongside `codegen`, `harness` and
`assertions`. The arm is its own rather than sharing `endvaridentity`'s for
this matrix's standing reason: the two gates guard DIFFERENT constructions
(a third POSITION view against `\z`; a CLASS view plus an alphabet refinement
plus three start states against `\b`), they use different reference knobs, and
a sabotage of one must not be reported as coverage by the other.

Two of the four are SEMANTICS-PRESERVING and two are not, which is the useful
way to read them:

- **S71** (alphabet refinement made unconditional) and **S73** (the
  class-indexed accept moved above its `pos >= n` guard) change NO answer.
  S71's refined alphabet is still the same partition more finely cut, so every
  matcher answers identically and only the byte-identity gate can see it.
  S73's out-of-bounds read at `pos == n` usually lands on a readable byte
  whose class carries the same bit, so the corpus goes green while the
  artifact has acquired UB — K27's class in generated code, and the reason
  rule 1 is checked structurally rather than by running anything.
- **S72** (the reverse skip's blind `match_start_position = pp;` restored) and **S74**
  (mechanism 4's reverse TERMINATION removed) change answers, but only on
  narrow populations that had to be built deliberately. S74 is the sharpest
  row in the wave: `\b` is safe by ACCIDENT at that boundary — its blind
  assumption coincides with its truth condition — so the sabotage is invisible
  to every leading-`\b` pattern and to every trailing-assertion pattern, and
  is seen only by LEADING `\B` at `startpos > 0`. That is why
  tests/assertions/wordb_basic.rxt carries those cells (wordb.rxt's shard
  holding the plain leading/trailing forms, split 2026-08-21) and why the
  wave's differential is split into arms at all.

S71 is also the shape of a mistake that would really happen: nobody deletes a
gate on purpose, but someone moves the word-set refinement next to the other
refinements in `eqclasses`, where every neighbour is unconditional, and the
diff looks tidier than what it replaced.

**S75** is the fifth and the cheapest to detect, and it is here for what it
says about the CHECK rather than about the code: pointing `\b` at a different
generated byte set leaves the artifact holding exactly one WORD bitmap (from
`\w`), so a rule counting copies of that bitmap passes. The rule needed a
second assertion — `(\b\w+\b)` must emit exactly ONE class table in total,
since both constructs must resolve to the same pooled set — and this row is
the measurement that the second assertion is not redundant. The corpus sees
this one loudly, which makes it a weaker row than S71/S73; it earns its place
because §7.2's argument is about a drift that has not happened yet, and would
survive two sets that happen to agree on today's alphabet.

## [M6.2 wave C] S76-S78 and S81, and two more arms

FOUR rows for `(?m)`, running two new arms — `mlinectxidentity`
(tests/codegen/run_mlinectx_identity.sh) and `mlinediff`
(tests/assertions/run_mline_diff.sh) — alongside `harness` and `assertions`.
Each arm is its own for this matrix's standing reason: the three identity
gates guard DIFFERENT constructions against DIFFERENT reference knobs, and
`mlinediff` is the only instrument in the tree that sweeps a generated subject
space over patterns with LIVE scan-avoidance mechanisms.

**THE WAVE PROPOSED SIX ROWS AND SHIPPED FOUR, and the two it dropped are the
most useful thing in this section.** §3.6.1 names five scan-avoidance
mechanisms; wave C wrote a row per mechanism, then MEASURED each before
committing it, by sweeping every corpus pattern whose ARTIFACT the edit
changes through 107 subjects under the §3.1 find-all loop:

| proposed row | mechanism | artifacts changed | answers changed | verdict |
|---|---|---|---|---|
| S78 | forward/reverse self-loop skip (rows 3, 5) | 11 | **3 cells** | SHIPS |
| S79 | `start_acc` narrowed (rows 1, 2) | 21 | **0** of 2,247 | DROPPED |
| S80 | compensating accept re-emitted (row 4) | 13 | **0** of 1,391 | DROPPED |

**S79 and S80 are not weak rows — they are NOT ROWS**, and shipping them would
have been the exact failure this directory exists to prevent: a sabotage with
no measured failing direction is a check that cannot fail. The reasons are
worth keeping because both are proofs, not accidents:

- **`start_acc`'s widening is REDUNDANT under D3's accept-pruning.** The
  unanchored start self-loop is the lowest-priority thread, so any closure
  reaching ACCEPT prunes it — therefore a class the start state accepts on
  cannot transition back to the start state, so it ESCAPES, so the
  prefilter's stay set never contains it. `src/gen/emit_dfa.c` already makes
  that argument for the neighbouring `last == (size_t)-1` gate and records
  that two critics attacked it without building a witness. §3.6.1's
  prediction that a narrowed `start_acc` costs `\bx*` three of its four
  matches is simply false.
- **The compensating accept can only UNDER-report.** It records the state's
  UPC_PLAIN accept at the skip's landing position, which is never greater
  than the correct bit (the EOL view's closure is a superset of the base's,
  and a skip-eligible state's accept does not vary by class). Combining it
  with S78 produced no divergence S78 did not already produce.

Of the four that shipped:

- **S77 is D62's control 2 and it is PERMANENT.** D62 chose a FIELD over a
  node kind and accepted a named residual: a new kind cannot be silently
  ignored, a new field warns nowhere. This row is the compile alarm's
  replacement for the KNOWN consumer.
  **ITS CELL MUST BE CAPTURE-BEARING, and finding that out is wave B's S75
  lesson arriving one wave later.** Possessification is a VM optimization —
  it removes backtracking states, and A DFA HAS NO BACKTRACKING TO REMOVE —
  so §8.7's own capture-free spelling `(?m)[^c]{1,3}$` routes to the DFA and
  answers correctly with the flag-read turned off (measured: 749 find-all
  cells, 0 divergences). One parenthesis routes it to the VM and the same
  pattern loses its match entirely. tests/assertions/multiline.rxt carries
  BOTH forms in adjacent sections and says which is which.
- **S76** (the newline alphabet refinement made unconditional) is
  SEMANTICS-PRESERVING in exactly S71's way and for the same reason — a
  refined alphabet is the same partition more finely cut — so the whole
  corpus and both oracles stay green and only the byte-identity gate can see
  it. Wave C makes the mistake likelier than wave B did: the two refinements
  now sit on ADJACENT LINES, one gated on `has_word` and one on `has_nl`,
  next to an ungated loop.
- **S78 needs a `(?m)$`-family pattern to fire at all**, which is R30 E5's
  finding turned into a row. `\b` cannot make it fire: its left operand is
  part of the state identity, so it is constant across any skipped run. A
  wave B sabotage of this line would have had NO FAILING DIRECTION in the
  wave the design calls most dangerous, which is why the design MOVED it
  here. Its three witness subjects (`"\n\nc"`, `"a\nb\nc"`) were added to the
  corpus WHEN THE ROW WAS VALIDATED — the first draft had neither, and this
  row would have come back UNDETECTED against single-newline subjects.
- **S81 writes the DESIGN'S OWN SENTENCE as code**, and that is what makes it
  worth its runtime. §3.7.2 says a `(?m)^`-anchored attempt "can only begin at
  offset 0 or immediately after a `'\n'`" — true of a fully-anchored pattern,
  false of `(?m)^a|b`. The shipped derivation asks which seeded start states
  are LIVE and gets both right; the sabotage asks for the newline set and
  loses the other branch's matches (`a|^b` on `"cac"`: `[(1,2)]` becomes
  `[]`; multiline.rxt goes 3241 pass / **39 FAIL** across seven patterns, every
  failure a lost match). Note its population includes PRE-EXISTING patterns — `^a|b`,
  `a|^b`, `(?:^|\b)foo` — so the derivation guards shapes that predate this
  wave. A row whose edit is a quotation from the design is the sharpest kind
  this matrix carries.

## [M6.2 wave D] S82-S84, two more arms, and a finding ABOUT THIS DIRECTORY

Three rows for `\G`, running two new arms — `gstartidentity`
(tests/codegen/run_gstart_identity.sh) and `gstartdiff`
(tests/assertions/run_gstart_diff.sh) — alongside `harness` and `assertions`.
Own arms for this matrix's standing reason; `gstartdiff` is additionally the
only instrument in the tree that drives docs/spec/match_api.md §3.1's FIND-ALL
LOOP against libpcre2 driven through the same loop, and the only one that
compares the two ENTRIES of one artifact.

- **S82** is a LOST MATCH living in the INTERSECTION of two waves, which is
  why neither wave's own population could have found it. Wave C's D63
  prefilter derives its candidate set from `s1u[]` (the states an attempt at
  `start > startpos` enters) and bounds its skip at `start > 0`; wave D adds
  `s1g[]` for the one attempt at `start == startpos`, which that derivation
  never looked at. A FULLY-`\G` pattern emits no prefilter at all and a
  `(?m)`-only pattern has no `s1g[]`, so the defect is reachable only by a
  pattern with BOTH — `(?m)^a|\Gb` on `"xb"` at startpos 1, which loses its
  match under the wave-C bound. **MEASURED: `corpus` 3 fail / 297 pass,
  `gstartdiff` 1 fail / 7 pass — DETECTED.**
  **Its first canonical run scored `gstartdiff: 0 fail`, and the finding was
  about the POPULATION**: the sweep's pattern list had no spelling carrying
  BOTH a `(?m)^` branch and a `\G` branch, so nothing in it emitted a memchr
  and a `\G` start family together, and only gpos.rxt caught a sabotage that
  loses matches. Three such patterns were added and the row re-measured. That
  is S48's and S78's lesson arriving on a third instrument — and it is the
  argument for running a row through the canonical driver before believing a
  hand-validated failing direction.
- **S84** is D47.5's failure mode one construct over, and it is here because
  the WRONG generalisation is the attractive one: `\z` takes the `$`-follow
  exemption with no gate because its satisfying set is the singleton `{n}`,
  and `\G`'s is the singleton `{startpos}` — so "singleton, therefore exempt"
  reads as an argument and is not one. Upward closure is the argument: `\z`'s
  singleton is ABOVE every retreat position and `\G`'s is BELOW every one.
  **MEASURED: `assertions` 1 fail** (the STRATS row reads 0x1 instead of 0x2)
  and **`harness` 15 fail** on gpos.rxt section 7, whose cells were added
  BECAUSE this row needs an answer-level failing direction and not only a
  stamp-level one.
- **S83** is the byte-identity row, SEMANTICS-PRESERVING in S69/S71/S76's way:
  every ENG_ATTEMPT artifact takes the three-way `\G` dispatch, all three arms
  lead to the same label on a `\G`-free machine, and no answer moves anywhere.
  **MEASURED: 93 of 1,175 `\G`-free corpus patterns change bytes; the whole
  `.rxt` corpus stays green.**

**AND THE FINDING THIS DIRECTORY SHOULD READ FIRST.** S83's first form came
back with the identity sweep at **1175/1175 IDENTICAL** — i.e. UNDETECTED by
the gate it exists for — and the cause is structural rather than particular to
the row. `run_*_identity.sh` builds its reference compiler from THE TREE'S OWN
SOURCES with a `-D` knob, so under a sabotage BOTH builds are sabotaged, and
any edit outside the code the knob actually suppresses applies to both sides
and CANCELS. Only sabotages living inside the knob's own gated region are
visible.

It is not specific to wave D. **MEASURED on wave B's S71 by this lane:
`run_wordctx_identity.sh`'s identity sweep stays 1135/1135 IDENTICAL under
it**, and that script fails only because deleting the `if (has_word)` gate
orphans a parameter, so the reference build emits `-Wunused-parameter` and the
script's own "the reference build produced warnings" check fires. The row is
therefore scored DETECTED for a reason unrelated to what its `SAB_DOC_FIGURE`
claims — and a future sabotage of the same shape that did not happen to orphan
a parameter would be scored UNDETECTED while the gate reported clean. S71 and
S76 now carry annotations saying so.

Wave D's own knob was moved to `src/gen/emit_dfa.c`'s three EMITTER decision
points, which makes the reference build structurally the pre-wave EMITTER
rather than an analysis with one fact suppressed — after which S83 goes red in
the sweep as it should. **Doing so immediately exposed a real defect in wave
D's own emitter that the mis-placed knob had hidden** (a dead `gseed[]` table
on every `\b`/`(?m)` artifact).

**RE-PLACED 2026-08-19 BY THE [M6.2] REPAIR SLICE, AND THE FIX IS NOT THE ONE
THIS SECTION PREDICTED.** "Move the knob to the emitter" is sufficient for
`\G` and NOT for `\z`/`\b`/`(?m)`, because it is the STAGE THAT DECIDES THE
EMITTED TEXT that has to carry the knob. `\G` refines no alphabet and interns
no state the emitter cannot neutralize. `\b` and `(?m)` refine the ALPHABET
and `\z` interns a STATE, and no emitter branch can un-refine a partition or
un-intern a state — so the reference build goes on emitting the sabotaged
class table. MEASURED by the slice, before it wrote anything: with an
emitter-only knob **S71 leaves 1186/1186 `\b`-free artifacts byte-identical**,
i.e. exactly as blind as the flag pin was. What works is a `#ifndef` around
the ANALYSIS'S ACTION — `eqclasses`' refinement, `make_state`'s interning —
which an edit to that action's own gate cannot cancel, plus the emitter half
for the sites the emitter really does decide. After both, all three rows are
red on their OWN gates, through BYTES rather than through the incidental
`-Wunused-parameter` (the `(void)` cast under the knob removes that path
too), with the corpus fully green — which is the semantics-preserving
signature these rows claim:

| row | canonical matrix cell | its identity population |
|---|---|---|
| S69 | `endvarid:1fail/2pass, corpus:0fail/32pass` | — (already at its action; did not move) |
| S71 | `wordctxid:1fail/2pass, corpus:0fail/20533pass` | 1178 of 1186 differing |
| S76 | `mlinectxid:1fail/3pass, corpus:0fail/20533pass` | 1117 of 1201 differing |

**THE RULE FOR THE NEXT KNOB-BASED GATE, which is what this whole section is
for:** put the knob around the ACTION the construct performs, never around
the FLAG that decides whether to perform it — a sabotage that deletes the
flag's consumer is the realistic edit, and it cancels a flag pin exactly. And
run the row through this driver rather than trusting the shape: every number
above is a measurement, and the 1186/1186 one refuted the plan the slice was
chartered with. **And verify the TREE a hand measurement was taken on**: the
slice's first S76 figure came back 1201/1201 identical, which looked like a
second refutation and was a stale extraction — the scratch tree it built
carried the PRE-slice `dfa.c`. Re-taken on a tree checked for the knob's own
`#ifndef` before building, the same edit moves 1117 of 1201.

Put beside S48 (green because the population could not reach the defect), S50
(green because the thing removed was not carrying the weight) and S60 (green
because the described defect does not exist in the shipped form), this is a
FOURTH kind of green: green because the CONTROL and the SUBJECT share a
source. That is the project's oldest recurring shape, and finding it inside the
directory that exists to prevent it is the second time that has happened
(compare the S19 expected-UNDETECTED account above).

## [M6.2 wave E] S85-S87, one new arm, and THREE ROWS WITH DISJOINT SYMPTOMS

Three rows for `\K`, running the new `kresetdiff` arm
(tests/assertions/run_kreset_diff.sh) alongside `codegen` and `harness`. Its
own arm for this matrix's standing reason, plus one specific to it: it is the
only instrument in the tree that asks libpcre2 the MATCH-HERE question — via
`\G(?:PAT)` at the same startpos, wave D's construct used as wave E's oracle
device — so it is the only thing that can see assertions_design.md §6.3
rule 3's two halves, the filter and the consumed-length return.

**WAVE E SHIPS NO BYTE-IDENTITY GATE, so these two rows and `codegen` carry
the whole failing-direction load between them.** Waves A-D each added a
`run_*_identity.sh` because each changed a construction spanning several
emitter decision points; `\K` is VM-forced and the emitter reads its counter
at exactly ONE site, so the claim is about one predicate and is pinned as
`[M6.2-KRESET rule 1b]`. That also means these rows have no S69/S71/S76/S83
sibling — no semantics-preserving row whose ONLY instrument is a byte
comparison — which is why both of them are visible in the corpus as well.

- **S85 is R30 C3's own request, word for word**: "make the emitted `\K`
  artifact write `caps[0][0]` from the prefilter's span; the structural check
  must go red. Without this it is the only module check with no measured
  failing direction." The panel asked for the row before the check existed.
  Under the hybrid, `caps_out`'s `start` argument IS `win[0][0]`, the reverse
  pass's answer, so forcing the pre-wave arm makes every `\K` artifact report
  where matching BEGAN. **CANONICAL MATRIX RUN:
  `codegen:1fail/55pass, corpus:210fail/386pass, kresetdiff:6fail/3pass` —
  DETECTED.**
- **S86 writes `slot_values[0]` DIRECTLY instead of through `<PREFIX>_SET`**, so the
  write is never trailed and cannot be undone. **CANONICAL MATRIX RUN: `codegen:1fail/55pass,
  corpus:6fail/590pass, kresetdiff:3fail/6pass` — DETECTED** — and the SIX is the number worth
  reading. A wrong-PROVENANCE bug is wrong nearly everywhere; a missing-UNDO
  bug is wrong only where a `\K` is crossed on a path that then LOSES, which
  is six cases in the corpus. That is the argument for writing those
  two families deliberately rather than trusting a subject sweep to wander
  into them, and it is why the two rows are separate: their symptoms inside
  `[M6.2-KRESET rule 1]` are DISJOINT (S85 fires the "does not read the slot"
  branch and leaves the write correct; S86 fires the "writes slot_values[0] directly"
  branch and leaves `caps_out` correct), so one row exercising both would let
  either branch rot behind the other.

- **S87 returns the zero Cost from `vm_cost`'s A_KRESET arm**, so the
  artifact's `trail_frames` is short by one entry per `\K` on the deepest
  path. Nothing is emitted differently and no answer changes: the artifact
  simply declares an array too small for the program beside it and returns
  `PCREC_ERR_FRAMES` on a pattern it can match. **CANONICAL MATRIX RUN: `codegen:0fail/56pass,
  corpus:33fail/563pass, kresetdiff:3fail/6pass` — DETECTED. The 0-fail codegen
  column is the driver CONFIRMING that all four `[M6.2-KRESET]` checks stay
  green, so "invisible to the structural checks" is a measurement rather than
  the author's claim.** It is the only one of the three the structural checks
  cannot see, and the reason is that they read emitted TEXT while this defect
  is in a NUMBER the emitter computed correctly and then under-declared.
  **Its population had to be BUILT.** `a\Kb` still compiles and still answers
  under it — one write fits the capacity anyway — and a subject chosen for
  LENGTH rather than for exceeding the repeat's COUNT never fills the trail
  either. `tests/assertions/kreset.rxt` section 11 exists for this row and
  says so in its own header; without it the count is 25 rather than 33, and
  the cells that fail would be section 4's loops reaching the bound
  incidentally rather than cells written to reach it.

**THE THREE SYMPTOMS ARE DISJOINT, which is why this is three rows and not
one edit with three halves.** S85 fires `[M6.2-KRESET rule 1]`'s "does not
read the trailed slot" branch and leaves the write correct; S86 fires the
same check's "writes slot_values[0] directly" branch and leaves `caps_out` correct;
S87 fires neither and is seen only by the corpus. Merging any two would let
the third's branch rot behind it.

All three were run through the canonical driver before handback — `1 rows
(undetected: 0, anomalies: 0, pc3-skipped: 0)` on each — rather than only
hand-applied, which is wave D's S82 lesson: a hand-validated failing direction
and the driver's can differ, and only the driver's is reproducible. Re-validate
with `bash tests/mech/run_sabotage_matrix.sh S85`, `S86` and `S87`.

## Rows with a documented history (retired and re-instated)

- **S108_rdshape_accepts_bref — RETIRED 2026-08-23 at the [M6.5] close, then
  RE-INSTATED the same hour as a TWO-SITE sabotage** (the matrix gained an
  optional second site; the single-site form below was measured
  unobservable and is kept as the record of why two sites are needed). Measured UNOBSERVABLE by the [M6.5.2] fix lane: the
  sabotage flips `rd_shape`'s verdict for a backreference body, but
  `pcrec_uniq_iteration`'s Glushkov arm (`possessify.c` `case A_BREF:
  g->ok = false`) independently declines every such body — the two gates
  are coextensive — so the reverse rung is never offered it and the
  emitted artifact is byte-identical to clean on the whole population.
  The wall in `rd_reverse` is real and fires when BOTH gates are removed,
  but the matrix applies ONE before/after hunk in ONE file, so that
  control is inexpressible today. A scored row that cannot go red is not
  a control, and the matrix has no expected-undetected mechanism; hence
  retired rather than left as a standing UNDETECTED. Residuals recorded
  on the [M6.5] close row: a multi-hunk sabotage mechanism, and a row for
  the Glushkov A_BREF arm itself (load-bearing for possessify, no row).
  Row numbering unchanged (S102-S107, S109-S120).

## [TT-8] the PROCS leak into inner suite sharding, fixed (2026-08-23)

`run_sabotage_matrix.sh`'s `PROCS` (row-level concurrency) was reaching the
`reject` and `harness` arms' OWN internal PROCS mechanisms undivided,
through the environment, rather than through the explicit `INNER_PROCS`
budget (`ncpu/PROCS`, the same formula `JOBS` already uses) those two arms'
command lines now carry. Measured live with `ps`/`/proc/<pid>/environ`
sampling, not only read from the dispatch code: a single-row `PROCS=4` run
of `S15` showed `run_reject_tests.sh` spawning 4 `REJECT_SHARD_TOTAL=4`
workers before the fix and 3 (`INNER_PROCS = 12/4`) after; `S15` and
`S107` both reproduce byte-identical fail/pass figures across leaked,
fixed, and genuinely-serial (no `PROCS` set) runs. Full account, the D69
evidence this lane also produced, and the manager's exact re-validation
commands: docs/testing.md's "[TT-8] the PROCS leak into inner suite
sharding, fixed" and "D69 — the mech re-run policy is TIERED" sections,
docs/dev/tt8_mech.md.

## D69 — the mech re-run policy is TIERED, and how to run it (2026-08-23)

Full matrix != every merge. `docs/dev/decisions.md` D69 tiers the re-run
obligation by what changed (docs-only -> tripwire; tests-only -> tripwire +
the changed rows; src changed -> tripwire + the rows whose `SAB_FILE` or
target changed; module/milestone CLOSE -> the full matrix), on the argument
that a row's verdict is a property of the pair (compiler, corpus) and this
lane's retro-diff of `build/mech_m64.log` (99 rows) against
`build/mech_m65.log` (118 rows) found ZERO rows flipping DETECTED ->
UNDETECTED without their own `SAB_FILE`/definition changing across 99 rows
in common — the measurement the ruling's risk acceptance rests on. The
tripwire is `python3 scripts/m6read_check_sab_anchors.py`; the rows for a
changed-files list are `bash tests/mech/rows_for.sh <path>...` (above).
Full tiers table, the anchor-drift/new-row accounting for the two
exceptions the retro-diff DID find (`S48`'s anchor-count fix, `S107`/
`S108` undetected-from-birth), and the earlier-journal corroboration:
docs/testing.md's "D69 — the mech re-run policy is TIERED, and how to run
it" section.

## [M6.6.2 wave E2] the `laexpand` arm, and the SEVEN ROWS IT CANNOT SEE

`tests/lookaround/run_expansion_diff.sh` (design §6.3) became a suite word on
2026-08-24. **Every row's assignment was MEASURED before it was made** — one
`laexpand`-ONLY mech run per row, so each cell below is what this arm sees ON
ITS OWN rather than what the row's other nets already saw:

| row | what it sabotages | `laexpand` |
|---|---|---|
| S122 | positive lookahead stops cutting | **UNDETECTED** |
| S123 | the entry cursor is not restored | DETECTED |
| S124 | negative lookaround fails without cutting | DETECTED |
| S125 | the negative form's `RX_PUSH` moves after the body | DETECTED |
| S126 | the `(?=` registry row loses `VM_ONLY` | DETECTED |
| S127 | `vm_nullable`'s `A_LOOK` arm answers false | DETECTED |
| S128 | `\K`-in-lookaround goes unchecked | **UNDETECTED** |
| S129 | `.negative` ignored | DETECTED |
| S130 | `.behind` ignored | DETECTED |
| S131 | `.atomic` ignored (design's S-LA16) | **UNDETECTED** |
| S132 | the follow is not scoped across the body | **UNDETECTED** |
| S133 | the back-step is inlined | **UNDETECTED** |
| S134 | the back-step sentinel goes unchecked | **UNDETECTED** |
| S135 | the back-step guard is clamped to `startpos` | DETECTED |
| S136 | the width rule accepts a variable body | **UNDETECTED** |

**8 DETECTED, 7 UNDETECTED, and the seven are the part worth reading.** They
are not a gap in the arm; they are a property of its POPULATION, and it is a
population nobody chose — it is whatever `tests/assertions/` happens to
contain, re-expressed through §6.1's nine definitions:

- **Every expansion in the table is an ATOMIC lookaround.** `(?*` and `(?<*`
  appear in none of them, so **S131 and S122** — the two rows about whether the
  cut is emitted — are invisible here however many cells run. S131 is design
  §9.3's S-LA16, and §11's wave-E2 landing bar asked for it to score DETECTED
  under this arm; **it does not, and the reason is structural rather than a
  shortfall in coverage.** It stays DETECTED by `harness` + `lookaround`, which
  is where the design assigned it and where `run_lookaround_diff.sh` §2's exact
  DISAGREEMENT count lives — the only arm in the tree that can see it at all.
- **Every expansion's lookbehind body is FIXED-WIDTH** (`\w`, `\n`, both width
  1), so **S136**'s widened width rule refuses nothing this population contains.
- **No expansion contains `\K`** — §6.1 rules `\K` out of the family and Q5
  counts the residual at 0 — so **S128** has nothing to bite on.
- **Every expansion's body is a SINGLE NODE with no follow to double-count**,
  so **S132**'s unscoped follow is a no-op over `\w`, `\n` and `\n?\z`.
- **S133 and S134** are structural rows whose own suites are `codegen harness`;
  the inlined back-step and the unchecked sentinel are behaviour-preserving on
  a one-byte back-step, which is the only kind this population has.

**ASSIGNING THE ARM TO THE SEVEN WOULD HAVE BOUGHT A BIGGER DENOMINATOR AND NO
EVIDENCE**, which is the shape this directory exists to refuse. The measurement
is the deliverable; the assignment follows it.

**THE WORKED EXAMPLE IS S130**, and it shows the driver's ATTRIBUTION working
rather than just its detection. Under `.behind` ignored, the arm reports:

    §1c the cell-fidelity guard      PASS   (arm B still answers all 8,260 cells
                                             exactly as tests/assertions/ states)
    the B == C attribution arm       PASS   (the FOLDED pattern still agrees
                                             with libpcre2 on all 8,260)
    §2 policy P1                     FAIL   1,737 of 8,260 cells: A != B and A != C
    §3 policy P2                     FAIL   2,242 of 12,543 cells: A != B and A != C
    §4 the --policy=none control     PASS   (all 263 patterns still trivially equal)

Read together those five lines say something no single failure count does:
the folded path is untouched, the control is untouched, and the ONLY thing that
moved is the lowering the substitution introduced. A green `B == C` beside a red
`A == C` localises the defect to the lookaround path before anyone opens a file.

**AND THE ARM FOUND A DEFECT IN THE DRIVER ITSELF, on this row**, which is
recorded because the guard that caught it is one a reader might otherwise think
decorative. `run_expansion_diff.sh`'s parent FAILS if a worker writes anything
to stderr. Under S130 it did: the witness printer passed the failing pattern to
`awk` through `-v`, which **escape-processes its assignments** — so it printed
`\G` as `G` and `\w` as `w`, i.e. a DIFFERENT PATTERN from the one that failed,
and warned while doing it. The patterns now travel in `ENVIRON`, which is not
escape-processed. A witness that misquotes the pattern is worse than no witness;
this was only visible on a run where something failed, which is why the arm's
first sabotaged run is when it surfaced.

**THE SKIP IS EXERCISED IN THE FAILING DIRECTION**, as `pc3`'s was. With the
oracle module moved aside, `run_expansion_diff.sh` prints its `SKIP:` banner and
`checks passed: 0 / checks failed: 0` — so a BARE scrape of those two numbers
records `laexpand:0fail/0pass`, `any_fail` stays clear, `any_ran` is set, and the
verdict block is then free to call the row **UNDETECTED**: a FINDING, produced by
an arm that never ran. The arm therefore tests for the `SKIP:` banner FIRST and
records `laexpand:SKIPPED-no-oracle` with `any_skip=1` instead. Both readings
were produced side by side from the same real log (2026-08-24):

    the BARE scrape      laexpand:0fail/0pass         -> would read as UNDETECTED
    the arm as wired     laexpand:SKIPPED-no-oracle   -> any_skip=1, any_ran unchanged

`laexpand` is the second arm here that can decline, so the verdict suffix now
NAMES the arms that skipped rather than assuming `pc3`.

## [DD-14 wave B+C] S143-S166 + S168, and the SEVEN ROWS THAT CERTIFY NOTHING

The wave that makes subroutine calls compile and match added 26 rows (S143-S166,
S168; S102 was RE-HOMED, see below). Final verdicts, all measured at the wave's
close on the branch's own tree:

| verdict | rows |
|---|---|
| **DETECTED (19)** | S102, S143, S144, S145, S146, S147, S148, S149, S154, S155, S156, S158, S159, S161, S162, S163, S165, S166, S168 |
| **UNDETECTED (7)** | S150, S151, S152, S153, S157, S160, S164 |

**[DD-14 WAVE E] S157 HAS SINCE CLOSED AS DETECTED — 20/6.** See the wave E
section at the end of this file. The row's own instruction ("if the matrix ever
reports NOW DETECTED here, some wave built that witness: re-measure, then flip
this to DETECTED") is what was followed, and the witness is the one the search
below had ruled out for the wrong reason. The table above is left as the
wave B+C reading, because the wave E finding is that the READING was
incomplete, not that the measurement was wrong.

**AN UNDETECTED ROW HERE IS NOT A REGRESSED GUARD.** This directory's standing
reading of `UNDETECTED` — "a guard regressed and is the thing to go fix" — is
right for a row whose population is known adequate. All seven of these are the
OTHER case: the sabotage was verified applied, the shipped behaviour is correct,
and the corpus contains no subject on which the removed thing is OBSERVABLE.
Each row carries its measurement and what is owed in its own `SAB_DOC_FIGURE`,
and each stays in the matrix so a later wave's cell can flip it. In one line each:

- **S150** (`W` drops the cut-mark family) — design §5.3b's axis-C was measured
  on a PROTOTYPE with ONE emitted copy of the atomic group. Under CALL_LINKAGE
  the lexical occurrence and the callee region are separate code with separate
  mark slots, so the clobber needs two REGION activations and an outer cut whose
  truncation matters — and the mis-read depth is LARGER, which discards fewer
  frames rather than resurrecting a match. The premise moved, not the guard.
- **S151 / S152** (`W` drops the empty-guard / span-counter families) — the wave
  ADDED cells that allocate both families in a recursive callee re-entered at two
  depths (the artifact legends name `RX_SLOT_EMPTY_GUARD0` and
  `RX_SLOT_SPAN_LOW0`), and the answers still do not move. So they are not
  undetected for want of a population. §9.3 told the implementation wave to
  "replace [the prediction] with the measured cell or DROP the row"; the wave
  replaced the population, could not produce the measurement, and kept the rows.
- **S153** (`W` drops the lookaround families) — the family §5.3b could not
  measure at all, because [M6.6.2] had not landed. Now measured on a lookahead
  inside a recursive callee live at two depths: no answer moves. P-12 P-2's
  withdrawal stands on the general argument, and the shipped `W` includes them.
- **S157** (possessify stops declining a call) — **the row's own target was
  wrong and the finding is which arm actually protects the corpus.** `(?&g)*+`
  never reaches `possessify.c`: parse.c desugars the possessive SUFFIX to
  `A_ATOMIC(A_REP(...))` and `vm_lifts` routes the cut, declining on
  `vm_nullable(r->l)` — the call-graph fixpoint, which is **S156's** arm and IS
  detected. possessify's decline governs AUTOMATIC possessification only, whose
  hang shape this corpus does not contain. **CLOSED AS DETECTED AT WAVE E** —
  the last clause is where the reading stopped a step early: the corpus does not
  contain the hang shape and never will, but the automatic path's failure is a
  DELETED MATCH rather than a hang, and that shape a corpus can hold. See the
  wave E section below.
- **S160** (revdet stops declining a call) — `rd_shape` is one of FIVE
  independent declines (`rd_reverse`'s own `ctx_fail`, `rd_alt_disjoint`,
  `vm_revdet_fits`), and no corpus quantifier body carrying a call is otherwise
  revdet-eligible: the rung wants a unique-iteration body, which a call's
  all-bytes FIRST set denies.
- **S164** (region slots uncounted) — the sabotage does not produce the
  out-of-bounds write the row predicts on this population; it produces a SLOT
  COLLISION (`RX_NSLOTS` 6 -> 5, a resume depth and a publish position sharing
  cell 4), and no cell reads both on one answer-changing path. The `asan` suite
  §9.3 assigns DOES NOT EXIST as a mech arm, so the memory-safety half was never
  scored either.

**FOUR ROWS WERE DEAD ON ARRIVAL AND THE MATRIX IS WHY WE KNOW.** S147 cleared
the complement of `W` instead of `W` (which is exactly what the callee writes,
so it changed nothing); S148's `k=2` bound is an assertion nothing sets, so the
row had to SEED it; S162 read `v->fmin`, which is already 0 at `vm_region`, so
it needed a two-site static to capture a real caller's follow; S159 aimed at
`pcrec_has_atomic`, which `mrl_win` short-circuits out of reach — re-pointed at
`pcrec_bref_mark` it went from UNDETECTED to 106 corpus failures. All four are
the same class: **a sabotage that removes something already unreachable proves
nothing about the guard it names**, and only running it says which one you wrote.

**S102 WAS RE-HOMED.** Its anchor sat in `select_engine.c` on a line this wave
rewrote (`fit.prefilter` now also refuses a call-bearing pattern). It is the
backref twin of the new **S165**, and both are DETECTED.

## [DD-14 wave E] S169, and S157 closing as DETECTED (20/6)

Wave E adds **one** row and flips **one**.

**S169 — `S169_root_minw_unchecked.sh`, the [DD-14.EMPTY] root check.**
`src/gen/emit_vm.c` stops emitting the search entry's ROOT minimum-width
comparison, so an empty-language pattern with no quantifier to carry an MRL
clamp runs until the resume-frame buffer gives up instead of answering NOMATCH.
**Its signature is a SPLIT one and that is the row's design**: exactly TWO of
`leftrec.rxt`'s three empty-language cells go red (the direct `^((?1)a)$` and
the indirect p/q cycle) and the third (`^(a?(?1)b)$`) stays GREEN, because its
`a?` emits an MRL clamp and it never depended on this site. **Three red means
the MRL machinery was cut, not this check** — a distinction no single-cell row
could make, and the reason the target is the whole file rather than one cell.

**S157 FLIPS TO DETECTED, and the interesting part is why the wave B+C search
missed the witness.** That search was right that `(?&g)*+` never reaches
`possessify.c`, and right that `possessify`'s decline governs only the
AUTOMATIC possessification of an ordinary quantifier. Where it stopped a step
early was in looking for the HANG. Under the sabotage the quantifier that gets
wrongly possessified is not the one over the call at all — it is the **`a?`
inside the callee**, made to look prefix-free by a call whose first set has been
emptied — and the consequence is a **deleted match**, which is a shape a corpus
can hold. MEASURED both ways on 2026-08-24 (clean binary vs. both-arms-
sabotaged, same tree, same flags):

| cell | subject | clean | sabotaged |
|---|---|---|---|
| `^(a?)(?1)+a$` | `"a"` | (0,1), group 1 = (0,0) | **NOMATCH** |
| `^(a?)(?1){2}a$` | `"a"` | (0,1) | **NOMATCH** |
| `^(a?)(?1)*$` | `"aaa"` | match | match — `RX_VM_STRATS` 0x2 → 0x3, **no answer moves** |

The third row is the general lesson and is kept in `quantified.rxt` for it: the
sabotage's most VISIBLE effect (a moved strategy stamp) is its least
OBSERVABLE one, and a witness cell built around the visible effect would have
left the row UNDETECTED for ever. **What makes the first two work is a
trailing literal that needs the `a` back** — the backtrack has to be
load-bearing before a possessification can delete anything.

**MEASURED, D69 tier 3, 2026-08-24 on `lane/srE` at `d0a8e36` (the lane's PRE-REBASE head; wave F touched none of these rows' `SAB_FILE`s or harness targets, so the reading carries)**: the 80 rows
`rows_for.sh` names for this lane's touched paths (`src/gen/emit_vm.c`,
`tests/recursion`, `tests/codegen`, `tests/prefilter`), run one row per
invocation at `PROCS=4` — **80/80 with `unexpected: 0`, `anomalies: 0`,
`oracle-skipped: 0`**. Six report `undetected: 1`, and they are exactly the
six the table above still lists: S150, S151, S152, S153, S160, S164. S157 is
DETECTED in that run. **S169** is DETECTED at `corpus:2fail/5pass` —
the two-red-one-green signature its own header predicts, arriving from a run
rather than from reading the row. **S165** is DETECTED at
`corpus:361fail/50pass, recdiff:18fail/1pass`.

**THE READING FOR OTHER `UNDETECTED` ROWS.** Six remain (S150, S151, S152,
S153, S160, S164). S157's closure does not make them likelier to close; it
changes what to try. The question a search should ask is not "can I reach the
failure the row's `SAB_DOC_FIGURE` predicts" but "what does the sabotage
actually do to an answer" — S157's predicted failure (a hang) was genuinely
unreachable and its real one (a deleted match) was two cells away.

## [DD-14 wave G] S173-S178, one row RE-POINTED and FLIPPED, and a row that found a real bug

Wave G adds **five** rows, adds a **sixth** whose expectation is UNDETECTED with
its search recorded, and **re-points and flips** one of wave B+C's.

**S173 — the splice shares the EXIT.** S-SR18's twin for the linkage S-SR18 does
not cover. `vm_splice` emits the inlined body straight to the CALL SITE's
continuation, so the `|W|` trailed restores after the exit are never reached and
the splice becomes capture-OPAQUE where §3.1 MEASURED a call to be
capture-TRANSPARENT. **Its detector must be a `g` line and this is the row where
that is not a style note**: the sabotaged matcher answers the same SPAN on almost
every cell, because a leaked capture moves what group 1 reports and not where the
match is. MEASURED: `captures.rxt` 20 passed / **2 FAILED**.

**S174 — the elision marks a LIVE group dead.** `pcrec_has_live_capture` prunes
at `rmin == 0` as well as `rmax == 0`, so every group under an OPTIONAL repeat is
declared dead, the pattern is handed to an engine that cannot record it, and the
span comes back UNSET on a match that is otherwise correct. **The polarity is why
the row exists**: over-reporting liveness costs an engine and never an answer, so
the failure that matters is the other direction. MEASURED:
`tests/captures/basic.rxt` 43 passed / **2 FAILED**.

**S175 — eligibility admits a RECURSIVE callee, AND IT FOUND A REAL BUG IN THE
WAVE IT WAS WRITTEN FOR.** `cg_eligibility` stops settling cyclic targets first,
so `reaches(i,i)` disqualifies nobody and a recursive callee is marked
`CALL_SPLICE`. **The first run SEGFAULTED the compiler** — a stack overflow in
`src/ir/nfa.c`'s `compile_ast`, not in the emitter, because that file's own
header claimed recursion depth was bounded by the parser's group-nesting cap and
**a call edge is not a nesting edge**. The wave added a splice-depth counter
there (the emitter already had two) and corrected the header in place. **A HANG
IS THE ONE FAILURE THIS MATRIX CANNOT REPORT** — it reads as an infrastructure
timeout — so a row whose prediction is a hang measures nothing, and closing that
is what the counter is for. MEASURED after the fix: `(a(?1)?b)` refuses with *"a
spliced subroutine call nested more than 1 deep… the splice eligibility rule
admitted a cycle"*, while `(a)(?1)` and `(x)(?1)` still COMPILE — the green half.

**S176 — the prefilter is built for a LINKED call.** S-SR17's twin one wave on:
wave E's row defends *"no prefilter for a call-bearing pattern"*, wave G narrowed
that to *"no prefilter for a pattern with a LINKED call"*, and this defends the
half that survived. MEASURED: `(a(?1)?b)` refuses with *"a LINKED subroutine call
reached the machine builder"*; `(a)(?1)` and `(x)(?1)` COMPILE. **The green half
is what separates this row from S-SR17** — wave E's version would have taken the
whole population red.

**S177 — the slot count misses a spliced site's save block.** K27's class for the
eighth slot family. MEASURED: `(a)(?1)` and `(x)(?1)` refuse with *"the splice
save block overflowed (3 of 0 slots)"*; the RECURSIVE `(a(?1)?b)` still COMPILES,
because its call takes the LINKAGE and allocates no splice block.

**S178 — the discharged root is not published, and it is expected UNDETECTED
WITH THE SEARCH RECORDED.** `pcrec_discharge_atomic` returns a NEW root when the
whole tree is the dischargeable group, and for the whole of [M6.4.2] that return
value was dropped: the call lived inside `pcrec_select_engine`, which assigned it
to a LOCAL, so selection judged the discharged tree while every later pass walked
the undischarged one. Wave G's pass hoist fixed it. **The search:** six patterns
whose ROOT is a dischargeable `A_ATOMIC` — `(?>[^"]*)`, `(?>a*+)`, `(?>(?:ab)*)`,
`(?>[^x]*)x`, `(?>a|ab)`, `(?>[^"]*+")` — emit BYTE-IDENTICAL artifacts before and
after, and the reason is structural rather than lucky: the discharge fires
exactly where `vm_lifts` LIFTS, and a lifted group allocates no mark of its own,
so deleted-before-the-emitter and lifted-away-by-the-emitter are the same
program. The row exists because the property it defends — selection and the
emitter walk ONE tree — has no other check, and a future rewrite with no lift
equivalent would make the drop real.

**S164 IS RE-POINTED AND FLIPS TO DETECTED**, and the reason it had to move is
the general lesson of this wave for this directory. Its cell,
`^(?:((?>a|ab))){0}(?1)z$`, names an ACYCLIC callee — which wave G SPLICES, so no
region is emitted, `rgn_emit[i]` is false and the sabotage is a **no-op on that
pattern**. **A row whose population has moved out from under it measures nothing,
and expected-UNDETECTED is the reading that hides that.** The fix is a cell whose
callee is IN A CYCLE, because in-a-cycle is what forces the LINKAGE and the
linkage is what emits a REGION for the pass to count:
`slotfamilies.rxt`'s `^(?:(?<g>(?=a)a(?&g)?b)){0}(?&g)$`, whose region body
carries a LOOKAROUND whose two slot families are per EMITTED COPY. **The
transcript of the flip:**

| | |
|---|---|
| shipped | `RX_NSLOTS 7`, with `RX_SLOT_LOOK_MARK0 = 5`, `RX_SLOT_LOOK_POS0 = 6` |
| sabotaged | `RX_NSLOTS 5`, both LOOK slots GONE and the two `RX_SET`s with them |
| `slotfamilies.rxt` | 45 passed / **2 FAILED** |
| the named cell | `"aaabbb"` expected `match 0 6`, got **`nomatch`** — A LOST MATCH |
| the OLD target, same sabotage | `zerodef.rxt` 33 passed / **0 failed** |

The last row is the pair that names the failure: green on the population it used
to have, red on the one it should have had all along.

**THE UNDETECTED TALLY MOVES BUT DOES NOT SHRINK.** Wave E left six (S150, S151,
S152, S153, S160, S164). S164 closes; S178 opens with its search recorded. Six
again, and a different six.

## [DD-14.FB] rows S179-S184, and two new suite words (2026-08-25)

Two words registered BEFORE the rows that need them, per the R31 C11 lesson
this file already records: **`framebuffer`** runs
`tests/recursion/run_frame_buffer.sh` and **`stackdepth`** runs
`tests/thread/run_stackdepth_tests.sh`. Neither folds into `harness`, for the
reason `vmidentity` gives for not being `codegen`: what they guard — that a
CALLER-SUPPLIED capacity is the one the matcher uses, and that the working
storage is off the entry's stack frame — is orthogonal to every answer-checking
cell in the corpus. `stackdepth`'s script prints a `KNOWN:` line on a green run
(K33, pinned by D73) and the scrape reads only its `checks passed:`/`checks
failed:` totals, which exclude it — so a pinned row can neither credit a row
with detection nor excuse one.

Two of the six rows are worth reading for what they say about the CELLS rather
than about the code:

- **S180** (each capacity bound to the other's array) is a NO-OP under any cell
  that supplies EQUAL capacities. The obvious corpus spelling,
  `frames-buffer=8192`, could never detect it — which is why
  `tests/recursion/framebuffer.rxt` hands over `1024,8192` for a subject
  needing 686 frames and 3,081 trail entries.
- **S184** (`_RESUME_FRAME_SIZE` stamped from the trail entry's layout) does
  not produce an under-allocated buffer at run time at all. The artifact
  carries a `_Static_assert` reconciling the stamped literal with the real
  `sizeof`, so the row's signature is a generated file that DOES NOT COMPILE,
  naming the macro. The design's §11 table proposed an ASan cell for this row;
  that would work and is the second line of defence, but the build-time
  detector fires first and is cheaper.

**Anchor drift this wave, recorded because it is the failure this directory
exists to make loud.** Splitting the run state moved four rows' anchors —
S89, S145, S155 and S168, all in `src/gen/emit_vm.c` — and they are re-anchored
here. Finding them turned up a FIFTH, **S174**, whose anchor in
`src/opt/atomic.c` had been stale since [DD-14.G]'s blocking fix (99eecd5)
respelled the guard it names: that row had been applying nothing, and
certifying nothing, for two commits. Re-anchored, with the history in its own
header, and NOT re-run since. `scripts/m6read_check_sab_anchors.py` reports
"all anchors resolve" as of this wave.
