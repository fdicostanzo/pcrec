# tri220 — TRIAGE of S220 UNEXPECTED in ucpu2's mech chain (2026-09-29)

Lane `tri220` (sonnet), read-only against `lane/ucpu2`'s running validation
chain, writing only inside its own worktree `worktrees/tri220` /
`lane/tri220`. Scope: diagnose why `bash tests/mech/run_sabotage_matrix.sh
S220` came back `***UNEXPECTED***` (rc=1) inside `/tmp/ucpu2s/final_chain.log`
(`mech_S220.log`), one of eleven rows [UCP] U2 (lane ucpu2) re-aimed after
replacing the fixed UPC class-context partition with a per-machine A_CTX
context-set list (`dbe52a55`).

## The finding, in one line

`/tmp/ucpu2s/mech_S220.log` reads `NOW DETECTED` —
`searchpinned:1fail/15pass, corpus:0fail/31197pass`, against the row's own
historical baseline `searchpinned:0fail/17pass, corpus:0fail/26883pass`. The
row was declared `SAB_EXPECT=UNDETECTED` since 2026-09-02/03: its own
2,850-pattern corpus sweep at the time found P2 (the start-pinned search
elision's view/context clause) discriminates EXACTLY three artifacts
(`\B`, `\B\B`, `\Bx*`), and all three are also SEED-NEEDING machines, so
P3's per-seed loop re-applies P1+P2 to every live seed and catches them
independently — a defence-in-depth pair, not two independent guards. Dropping
P2 only at the START state (this row's plant) was therefore provably inert.

## Was the re-aim wrong?

No. Ucpu2's own note on the row (`RE-AIMED 2026-09-29 BY [UCP] U2 (lane
ucpu2), intent re-verified: signature only: pcrec_state_view_invariant(fd,
st); the plant still drops P2`) is accurate. The mech run's own `pop`/`reach`
fields confirm it: the named manifest (`tests/codegen/manifests/
s220_view_decliners.txt`) still floors at exactly 3, and the reach probe
(`\bx*` still declines via P2 on the clean tree, `x*` still pins) still
reads `reach:ok(1/1)`. Neither moved. The re-aim is a correct, behaviour-
preserving edit of the plant's own site.

## Is the row's recorded expectation stale, or is this a real U2 regression?

Stale expectation, not a regression in the shipped compiler. Two reasons:

1. **Nothing about the row's own documented population changed.** The three
   named witnesses' clean-tree behaviour, and the reach probe that certifies
   it, are byte-for-byte what they were at the 2026-09-03 baseline.
2. **The corpus arm stays `0fail` even under the sabotaged tree**
   (`corpus:0fail/31197pass`) — nothing in the shipped, un-sabotaged compiler
   is broken by this finding. What moved is `run_search_pinned.sh`'s own
   internal check count (17 pass, 0 fail → 15 pass, 1 fail), meaning the
   SABOTAGE is now directly observable by that script where it previously
   was not — i.e. P2's start-state check has become load-bearing for some
   machine this compiler now builds that it did not build (or did not build
   the same way) before U2.

## The mechanism (reasoned from the tree, not from a rebuild — see "What is
## still owed" below)

`pcrec_state_view_invariant` (P2, `src/opt/scanedge.c`) tests accept
variance across every atom of `Dfa.natoms` uniformly — one loop, no
left/right distinction. `dfa_needs_seed` (P3's own gate, `src/gen/
emit_dfa.c:3310`) tests something narrower: whether the SEED TARGET STATE
(`s1u[u]`) differs across atoms — which is a question about the byte
*already consumed* (the preceding byte), because seeding only ever exists to
answer "what state do I start in when the search begins mid-subject, given
the class of `s[search_from-1]`". Historically the two were coextensive on
this corpus: `\b`/`\B` read BOTH the preceding and following byte's class,
so every pattern whose start-state accept varied by context (P2's own axis)
also needed seeding (P3's axis), and P3's per-seed re-check made P2's
start-state copy a defence-in-depth spare rather than the sole guard.

[UCP] U2 (`dbe52a55`) replaces the fixed four-atom UPC partition with a
per-machine LIST of context sets (`Dfa.ctx[]`), and `src/ir/dfa.c`'s
`CTXROW_CTX` contributor row (line 188) now reads *"an A_CTX set (`\b`/`\B`'s
word set, a ONE-CHARACTER LOOKAROUND's set)"* — the same U2 wave's abi
45 → 46 bump is titled *"one-character lookarounds move VM -> DFA"*.
`N_CTX`'s truth function (`dfa.c` ~line 953) tests the preceding and
following byte's atom membership SEPARATELY (`ctx_bit(cl->left,k)` /
`ctx_bit(cl->right,k)`), and a one-character LOOKAHEAD's context set reads
only the RIGHT (upcoming) side. A machine whose only live context set is
such a lookahead therefore never consults the LEFT side during closure, so
every `s1u[u]` interns to the identical state and `dfa_needs_seed` answers
**false** — while `pcrec_state_view_invariant` still, correctly, finds the
start state's accept varies across atoms (the lookahead's own condition).
P3's per-seed loop, gated on `dfa_needs_seed`, never runs for such a
machine, so P2's own start-state check — the one this row's plant deletes —
becomes the SOLE guard. That is exactly the shape S220's plant removes and
nothing downstream replaces, for a population this compiler did not build
before U2 widened what counts as an A_CTX contributor.

This is consistent with, and not contradicted by, the row's own prior
measurement: that 2026-09-02 sweep ran against a corpus and a compiler with
no such population (one-character lookarounds were VM-only then), so
"exactly three" was correct for the population that existed at the time.

## Was the exact failing witness inside `run_search_pinned.sh` identified?

**No, and that is stated plainly rather than guessed at.** None of the
script's own fixed witness lists (§1's fifteen named patterns, `DIFF_PATTERNS`,
`C3_PATTERNS`) contain a lookaround spelling, so if the new discriminating
population reaches this check, it most likely arrives through §9's shared
corpus extraction (`grep -rhE '^pattern ' tests/`, which now also sweeps
[UCP] U2's own new `tests/ucp/ctxnode.rxt`) rather than through a hand-written
witness — but that is a plausible route, not a confirmed one. Isolating the
exact witness needs a compiler built from the sabotaged tree, compared
against the clean one, which needs a build. **A `make -j4 CC=gcc-16` build in
this lane's own worktree was declined by the box's one-heavy-suite-at-a-time
concurrency guard** (the auto-mode classifier's "Interfere With Workloads"
denial) while ucpu2's own chain and this triage lane were both live on the
box, consistent with `BOILERPLATE.md`'s standing rule and the explicit
instruction in this lane's brief not to re-run mech. `VALIDATE_ONLY=1 bash
tests/mech/run_sabotage_matrix.sh S220` — a pure field-syntax check that
builds nothing — was run and passes clean (see "Validation" below); the
measurement itself (the `mech_S220.log` this report reads) came from the
manager's own scheduled chain, not from a run this lane launched.

**Owed to a build-capable follow-up**: re-derive P2's "exactly N artifacts"
corpus sweep (the row's own 2026-09-02 method — an instrumented stamp
reporting which clause declined, reverted before delivery) against the
current corpus and compiler, to name the real witness(es) and confirm the
population is what this report reasons it to be rather than something else
entirely.

## The fix (committed, confined to `tests/mech/`)

`tests/mech/sabotages/S220_pinned_view_clause_dropped.sh`:

- Removed the `SAB_EXPECT=UNDETECTED` line — the row now reads the default,
  `DETECTED`, matching the mech run's own measured verdict. Per this
  directory's standing rule ("re-measure it, then flip its SAB_EXPECT — do
  not simply delete the row, and do not leave the stale expectation
  standing"), the re-measurement is the mech run already captured in
  `/tmp/ucpu2s/mech_S220.log`, which this report cites verbatim.
- Appended the mechanism paragraph above to the row's header, dated and
  attributed to this lane, including the explicit "reasoned, not rebuilt"
  caveat and the owed follow-up.
- Appended the exact measured figures (`searchpinned:1fail/15pass,
  corpus:0fail/31197pass`, `unexpected: 1, undetected: 0, unreached: 0,
  anomalies: 0`) to `SAB_DOC_FIGURE`, in the same "MEASURED … RE-MEASURED …"
  chain the field's earlier entries already use.

Nothing else in the row changed: `SAB_ID`, `SAB_FILE`, `SAB_SUITES`,
`SAB_DESC`, `SAB_REACH`/`SAB_REACH_EXPECT`/`SAB_REACH_POP`, `SAB_COUNT`,
`SAB_BEFORE`/`SAB_AFTER` are untouched, and the ucpu2 re-aim's own
provenance line at the file's foot is left as ucpu2 wrote it.

## Validation

- `bash -n tests/mech/sabotages/S220_pinned_view_clause_dropped.sh` — clean.
- Sourced directly in a subshell: `SAB_EXPECT` reads empty (default
  `DETECTED`); `SAB_DOC_FIGURE` populates; no stray backtick in either
  double-quoted field (the directory's own recorded hazard — checked by
  grepping for backticks outside comment lines, none found in an assigned
  field).
- `VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S220` — `FIELDS
  OK (definition parses and every field validation passes; NO tree built, NO
  suite run, NOTHING measured)`, `1 definition(s) valid, 0 rows measured`.
  (This is the field-syntax-only mode — no build, no measurement — the
  brief's "do not re-run mech" instruction is read as covering the real
  measurement, which this lane did not launch.)
- The actual re-run of `bash tests/mech/run_sabotage_matrix.sh S220` against
  this fix (which should now read plain `DETECTED`, no `***UNEXPECTED***`) is
  **OWED to the manager**, once the box is free of the concurrent chain.

## What this is NOT

This is not evidence of a defect in [UCP] U2's shipped, un-sabotaged
compiler — the corpus arm stays `0fail` throughout, on both the clean and
the sabotaged tree, and P2 itself (the real, un-sabotaged code) still runs
at both the start state and every seed exactly as `emit_dfa.c` shows. The
finding is entirely about this ONE sabotage row's own expired claim that
P2's start-state copy is provably redundant with P3 — U2 widened the
population for which that is false.
