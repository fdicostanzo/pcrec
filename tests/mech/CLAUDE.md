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
  `reject` `harness` `registry` `pc3` `cli` `vmidentity` `vm`
  `endvaridentity` `assertions` `kresetdiff`, plus the per-lane arms listed
  below),
  `SAB_DESC`,
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
- `endvaridentity` → `tests/codegen/run_endvar_identity.sh`, [M6.2] wave A's
  byte-identity gate. Its own arm rather than `codegen` or `trie`, for the
  reason `vmidentity` is its own: "adding a THIRD closure view moved no byte
  of any pattern that does not use it" is orthogonal to every
  optimization-present check and to the trie's own equivalence. It builds a
  reference compiler and sweeps the whole corpus, so it is the most expensive
  arm here — assign it only where the signal really is emitted bytes.
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
