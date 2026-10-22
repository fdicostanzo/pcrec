# langfix3 — applying the langrev review of the pattern-language fix branches

Lane langfix3 (opus), 2026-10-22. Branch `lane/langfix2` (which contains
`lane/speclang` and `lane/langfix`), worktree `worktrees/langfix2`. Applies
the manager's dispositions of the pre-merge review (rulings file R2).

## STATE AT HANDOFF

- All code, tests, re-pins, comments and docs committed on `lane/langfix2`
  (WIP commits 9f6926d75, 08402f094, then this report).
- Rulings file `langfix2_rulings.md`: last entry applied is **R2**.
- Queue jobs 698-langfix2-test/-mech, 695-langfix-test, 696-langfix-mech and
  690-speclang-test were CANCELLED before the first commit. One chain on this
  branch validates all three branches.
- VALIDATION OWED (queued with `scripts/boxqueue add`, dry-runs passed; each
  `--ready` holds while `i2build-parity` is pending or running, tested both
  ways):
  - `699-langfix3-test`: make -j16, make strict, `scripts/perfrun --label
    langfix3` make test, then make's own red-line grep. Completion =
    `== 699 step verdict OK`; make's output in the run dir's `job.log.make`.
  - `699-langfix3-mech` (after langfix3-test): S23 S136 S1386-S1393
    S1450-S1455 S1490, 17 rows. Completion = `== mech run COMPLETE: 17 rows`.
  - `699-langfix3-k124diff` (after langfix3-test): item 2's proof,
    `build/lf3/k124diff.py`. Completion = `== k124diff COMPLETE: 0 failures`;
    per-pattern table `build/lf3/k124diff/movers.tsv`.
- Light validation done by hand: build and `make strict` clean; the harness on
  tests/recursion/inlookaround_self.rxt, tests/recursion/inlookaround.rxt,
  tests/modifiers/optrun_group.rxt, tests/atomic_groups/possessive_ungreedy.rxt
  (179 cases, 0 failed); `syntax_index_check.py` green at the floor and red
  with the floor raised by one; all five generated corpus files reproduce
  from their specs (four byte-identical, possessive_ungreedy.rxt gained only
  its trailing blank line).

## 1. K127: a nested lookbehind's calls are followed (MUST-FIX)

Premise reproduced: `((?<=(?2)))(a(?<=(?1)))` and the brief's three other
cells compiled on the branch; libpcre2 10.46 refuses all four with err 125.
`cg_length_calls` (src/opt/callgraph.c) now continues into an `A_LOOK` when it
is a lookbehind and stops only at a lookahead. Probes after the fix agree with
libpcre2 on refused/accepted for all ten cells tried (the four brief cells,
`((?<=(?2)))(a(?=(?1)))`, its `(?!` twin, `(?<=(?=(?<=(?R))))x`,
`(?<=a(?<=(?R)))x`, `(?<=(?<=(?1)))(a)`, `((?<=(?2)))(a(?=b(?<=(?1))))`).

Offsets: libpcre2 reports @1/@1/@1/@31 for the brief's cells; pcrec reports
@1/@1/@1/@19. Where a cycle runs through more than one lookbehind, the two
may blame different ones: `(?<=a(?<=(?R)))x` 5 vs 0,
`((?<=(?2)))(a(?=b(?<=(?1))))` 1 vs 17. pcrec always blames a lookbehind its
rule finds re-entering. The rows' comments record libpcre2's offsets. The
`.rxt` format's `perr` has no offset field.

Rule text corrected ("lookahead", not "lookaround") in internal.h
(`pcrec_callgraph_lookbehind_recurses`), callgraph.c, pattern_language.md
§7.4¶5a, the corpus header, tests/recursion/CLAUDE.md and K127's entry.
New rows in tests/recursion/inlookaround_self.rxt: the four perr cells, plus
ACCEPTED controls `((?<=(?2)))(a(?=(?1)))` and `((?<=(?2)))(a(?!(?1)))`.
On "aa" both libpcre2 (-52, recursion loop) and pcrec (-3) give up at match
time, so the controls carry only subjects that answer.

Sabotage: S1490 (new) reverts to "return at every A_LOOK"; the four new perr
rows catch it (that is the pre-fix code, which compiled them). S1455's anchor
moved with the code; it was re-anchored with the same intent (now: descend
into every A_LOOK, a lookahead too), so the two lookahead controls are its
witnesses.

## 2. K124: no previously-right pattern moves (MUST-FIX)

The first fix wrapped the flagged body in `A_CAT(body, A_EMPTY)` under every
group. Reproduced: `((?i))a` 542 -> 599 RX_VM_PROGRAM_BYTES, and
`x(?>(?i))y`, `(?<n>(?i))a\k<n>` moved too. Now `pcrec_wrap_bare_anchor`
CLEARS the flag in place on a non-anchor body (a bare option run is an
A_EMPTY whose flag only the quantifier check reads), and keeps the CAT wrap
for bare anchors exactly as before. This is the reviewer's "flag-clear"
option. It is one mechanism for every group, and the capturing/atomic/named
paths need no case of their own. Measured by hand against a merge-base build
(62ca83389, `build/lf3/base/`): the three cells, `(^)*a` and `(?:\b)*a` are
byte-identical (.c and .h), and `(?:(?i))*a`, `((?i))*a`, `(?i:(?s))*b`,
`(?>(?i))+b`, `(?<n>(?i))*a` now compile. `a(?i)*` stays err 109. The STOP
RULE did not fire.

The corpus-wide proof is the queued `699-langfix3-k124diff`. It compares old
and new emitted C over every `--list-source` pattern plus 13 option-run
cells, at the default engine and `--engine=vm`, in byte and `-e utf8`. Every
mover (both compile, bytes differ) must be attributed by a declared table to
a branch fix of a wrong answer (K122 possessive under `(?U)`, K115 `(?x)`
Unicode space under utf8). An unattributed mover, a moved review cell, a new
refusal that is not K127's shape, or a population below 3,000 both-compile
rows FAILS. A planted copy of the old wrap would show the three cells as
movers (measured above), so it would fail. S1452 was re-anchored the same
way (it now drops the flag clear).

## 3. Comments only (NOTE)

lower_enc.c's `A_CAT(A_EMPTY, alt)` seal comment now says it is redundant
since K123 and kept because removing it is an abi event. emit_vm.c's
`vm_look_behind` comment now describes `pcrec_lookbehind_branches` (exactly
`nbranch - 1` spine nodes peeled, branch 0 may be an alternation, a SHORT
spine fails) in place of the old spine walk. parse.c's `p_group_body` and
bare-anchor predicate comments no longer claim the flag propagates, or that
`(?:(?i))*` is err 109.

PLAN CANDIDATE (simplification, rides the next abi event): remove
src/opt/lower_enc.c's `A_CAT(A_EMPTY, alt)` seal around a multi-branch
UTF-8 class replacement. It has been redundant since K123's
`pcrec_lookbehind_branches`. Removing it moves emitted bytes, so it belongs
inside an abi bump.

## 4. Generator tracked, syntax-index floor (NOTE)

`tests/lib/p2gen.py` and `tests/lib/p2probe.c` are the lane's
`build/lf2/gen.py` and `p2probe.c`, made repo-relative. The probe is built
on demand into `build/p2gen/`. A new block key `eng` emits `engine vm`.
Each generated corpus's spec sits beside it as `<name>.gen.py`:
possessive_ungreedy, lookbehind_group_alt, optrun_group, octal_wide,
inlookaround_self. The possessive_ungreedy spec now states the post-processing
that langfix2 had done by hand (the `classes` feature, the engine-vm twin of
every block). The three langfix files (xmode_utf8, utf8_names,
xbrace_space) had no generator: they were written by hand against the oracle,
so there is nothing to commit for them (the brief counted 7 files; 5 were
gen.py-produced). `tests/registry/syntax_index_check.py` has
`ROWS_FLOOR = 142`, and its population line fails below it.

## Re-pins

tests/rxtsource/run_rxtsource_tests.sh: CENSUS/RUNSH blocks 5926 -> 5932,
lines 71492 -> 71502; C3_PASS 20424 -> 20428, C3_SKIP 50982 -> 50988,
C3_SKIP_NOPYTHON 2212 -> 2218, C3_VERIFIABLE 22650 -> 22660. These were
measured with the census awk and with verify_rxt.py on the old and new
inlookaround_self.rxt alone. Other population pins (start-set manifests,
size tripwires) were not checked by hand. The queued make test reads them.

## 5. Candidates (not in scope)

- `\p{Xyz}` refusal wording (D26/K118 tier).
- The pre-existing `\x{ }` offsets.
- K127 blame offsets on multi-lookbehind cycles (above). It is diagnostic
  position only, probably D26 tier.
